from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import requests
import hashlib
import hmac
from django.http import HttpResponse
from Keys.keys import keys
from django.http import JsonResponse

@csrf_exempt
def formtoken(request):
    #URL de Web Service REST
    url = 'https://api.micuentaweb.pe/api-payment/V4/Charge/CreatePayment'

    #Encabezado Basic con concatenación de "usuario:contraseña" en base64
    auth = 'Basic ' + base64.b64encode(f"{keys["USERNAME"]}:{keys["PASSWORD"]}".encode('utf-8')).decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth,
    }

    parameters = json.loads(request.body)

    data = {
        "amount": int(float(parameters['amount']) * 100),
        "currency": parameters['currency'],
        "orderId": parameters['orderId'],
        "customer": {
            "email": parameters['email'],
            "firstName": parameters['firstName'],
            "lastName": parameters['lastName'],
            "phoneNumber": parameters['phoneNumber'],
            "identityType": parameters['identityType'],
            "identityCode": parameters['identityCode'],
            "address": parameters['address'],
            "country": parameters['country'],
            "state": parameters['state'],
            "city": parameters['city'],
            "zipCode": parameters['zipCode'],    
        }
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data['status'] != 'SUCCESS':
        raise Exception
    
    formToken = response_data['answer']['formToken']
    return JsonResponse({'formToken': formToken, 'publicKey': keys['PUBLIC_KEY']})

@csrf_exempt
def validate(request):
    data = json.loads(request.body)
    if not data: 
        raise Exception("No post data received!")

    validate = checkHash(data, keys["HMACSHA256"])

    return JsonResponse(validate, safe=False)

@csrf_exempt
def ipn(request):
    if not request.POST: 
        raise Exception("No post data received!")

    #Validación de firma en IPN
    if not checkHash(request.POST, keys["PASSWORD"]) : 
        raise Exception("Invalid signature")
    
    answer = json.loads(request.POST['kr-answer']) 
    transaction = answer['transactions'][0]

    #Verificar orderStatus: PAID / UNPAID
    orderStatus = answer['orderStatus']
    orderId = answer['orderDetails']['orderId']
    transactionUuid = transaction['uuid']

    return HttpResponse(status=200, content=f"OK! OrderStatus is {orderStatus} ")

def checkHash(response, key):

    answer = response['kr-answer'].encode('utf-8')

    calculateHash = hmac.new(key.encode('utf-8'), answer, hashlib.sha256).hexdigest()

    return calculateHash == response['kr-hash']