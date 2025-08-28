from django.shortcuts import render
from .models import User, Listing, Booking, Review, Payment
from rest_framework import viewsets
from .serializers import UserSerializer, ListingSerializer, BookingSerializer, ReviewSerializer
import uuid
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Create your views here.

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(user=request.user)

        # Trigger Celery task
        send_booking_email.delay(request.user.email, booking.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED) 




# Initializes a new payment

class InitiatePaymentView(APIView):
    def post(self, request):
        user = request.user
        amount = request.data.get("amount")
        booking_reference = str(uuid.uuid4())

        # Create pending payment record
        payment = Payment.objects.create(
            user=user,
            booking_reference=booking_reference,
            amount=amount,
            status="Pending"
        )

        # Chapa request data
        data = {
            "amount": str(amount),
            "currency": "ETB",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tx_ref": booking_reference,
            "callback_url": f"http://localhost:8000/api/payments/verify/{booking_reference}/",
            "return_url": "http://localhost:8000/payment-success/",
            "customization[title]": "Booking Payment",
            "customization[description]": "Payment for travel booking",
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        response = requests.post(
            f"{settings.CHAPA_BASE_URL}/transaction/initialize",
            headers=headers,
            data=data
        )

        resp_json = response.json()

        if resp_json.get("status") == "success":
            payment.transaction_id = booking_reference
            payment.save()
            return Response({"payment_url": resp_json["data"]["checkout_url"]})
        else:
            return Response(resp_json, status=status.HTTP_400_BAD_REQUEST)
        


class VerifyPaymentView(APIView):
    def get(self, request, booking_reference):
        try:
            payment = Payment.objects.get(booking_reference=booking_reference)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        verify_url = f"{settings.CHAPA_BASE_URL}/transaction/verify/{booking_reference}"
        response = requests.get(verify_url, headers=headers)
        resp_json = response.json()

        if resp_json.get("status") == "success" and resp_json["data"]["status"] == "success":
            payment.status = "Completed"
            payment.save()
            # Optionally, you can send a confirmation email or perform other actions here
            from django.core.mail import send_mail
            send_mail(
                "Payment Confirmation",
                "Your booking payment was successful!",
                "noreply@mytravel.com",
                [payment.user.email],
                        )

            return Response({"message": "Payment verified successfully"})
        else:
            payment.status = "Failed"
            payment.save()
            return Response({"message": "Payment verification failed"}, status=400)