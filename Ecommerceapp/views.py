from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters

from .models import User, Product, Category, Order, Payment

from .serializers import UserSerializer, ProductSerializer, OrderSerializer, PaymentSerializer


def home_view(request):
    return JsonResponse({"message": "Welcome to the E-Commerce API! Use '/api/' routes to interact with the system."})


# class UserRegistrationViews(CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]
#
#     def perform_create(self, serializer):
#         password = self.request.data.get("password")
#         try:
#             validate_password(password)
#         except ValidationError as e:
#             raise ValidationError({'password': e.messages})
#         user = serializer.save()
#         return user
#
#     def create(self, request, *args, **kwargs):
#         serialzer = self.get_serializer(data=request.data)
#         if serialzer.is_valid():
#             self.perform_create(serialzer)
#             return Response({
#                 'messages': 'Successfully Created',
#                 'user_id': serialzer.instance.id
#             }, status=status.HTTP_201_CREATED)
#         return Response(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=201)
    return Response(serializer.errors, status=400)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']
    pagination_class = PageNumberPagination


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


#
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
#
#
# @csrf_exempt  # Disable CSRF for this example (not recommended in production)
# def payment_form(request):
#     if request.method == "POST":
#         # Handle form submission here
#         data = request.POST
#         # Example: process the form data
#         pp_Version = data.get("pp_Version")
#         pp_TxnRefNo = data.get("pp_TxnRefNo")
#         pp_Amount = data.get("pp_Amount")
#         # Additional processing logic
#
#         # Redirect or render a success page
#         return render(request, "payment_success.html", {"data": data})
#
#     return render(request, "index.html")


from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from datetime import datetime, timedelta
import hashlib
import hmac

# Configuration
JAZZCASH_MERCHANT_ID = "MC146795"
JAZZCASH_PASSWORD = "s04x3eugtt"
JAZZCASH_RETURN_URL = "http://127.0.0.1:8000/success/"
JAZZCASH_INTEGRITY_SALT = "44yv9y7u52"


def checkout(request):
    # product_id = request.GET.get('product_id')

    product_name = "Laptop"
    product_price = 100, 000, 000, 000

    pp_Amount = int(product_price)

    # Get the current date and time
    current_datetime = datetime.now()
    pp_TxnDateTime = current_datetime.strftime('%Y%m%d%H%M%S')

    # Create expiry date and time by adding one hour to the current date and time
    expiry_datetime = current_datetime + timedelta(hours=1)
    pp_TxnExpiryDateTime = expiry_datetime.strftime('%Y%m%d%H%M%S')

    pp_TxnRefNo = 'T' + pp_TxnDateTime

    post_data = {
        "pp_Version": "1.0",
        "pp_TxnType": "",
        "pp_Language": "EN",
        "pp_MerchantID": JAZZCASH_MERCHANT_ID,
        "pp_SubMerchantID": "",
        "pp_Password": JAZZCASH_PASSWORD,
        "pp_BankID": "TBANK",
        "pp_ProductID": "RETL",
        "pp_TxnRefNo": pp_TxnRefNo,
        "pp_Amount": pp_Amount,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": pp_TxnDateTime,
        "pp_BillReference": "billRef",
        "pp_Description": "Description of transaction",
        "pp_TxnExpiryDateTime": pp_TxnExpiryDateTime,
        "pp_ReturnURL": JAZZCASH_RETURN_URL,
        "pp_SecureHash": "",
        "ppmpf_1": "1",
        "ppmpf_2": "2",
        "ppmpf_3": "3",
        "ppmpf_4": "4",
        "ppmpf_5": "5"
    }

    sorted_string = '&'.join(f"{key}={value}" for key, value in sorted(post_data.items()) if value != "")
    pp_SecureHash = hmac.new(
        JAZZCASH_INTEGRITY_SALT.encode(),
        sorted_string.encode(),
        hashlib.sha256
    ).hexdigest()
    post_data['pp_SecureHash'] = pp_SecureHash

    return render(request, 'index.html',
                  {'product_name': product_name, 'product_price': product_price, 'post_data': post_data})


@csrf_exempt
def success(request):
    return render(request, 'success.html')
