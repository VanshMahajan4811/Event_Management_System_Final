from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from datetime import timedelta
from django.shortcuts import render, redirect

import requests  # Added import for HTTP requests

# To send Mail and SMS Msg
from django.core.mail import send_mail
# from twilio.rest import Client        
from EventManager import settings
from EventManager.settings import EMAIL_HOST_USER

from EM_App.models import Event, Participant

# To add neccesary date check-up while recieving form details
import datetime as dt

# Import DRF modules
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ModelSerializer

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

# Serializer for Event model
class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


@api_view(['GET'])
def event_api(request):
    """
    API endpoint that returns list of events in JSON format
    """
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

# Signup view
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not email or not password:
            messages.error(request, "Please fill in all fields.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "User already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "User registered successfully. Please log in.")
        return redirect('login')

    return render(request, 'signup.html')

# Login view

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if not username or not email or not password1 or not password2 or not role:
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        if role == 'admin':
            user.is_staff = True
        user.save()

        logout(request)
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('index')

    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        # Log out current user to allow login as different user
        print(f"User already authenticated: {request.user.username}, logging out to allow new login.")
        logout(request)

    form = AuthenticationForm()

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)  # This line is correct, login takes request and user
                # Refresh user object from database to get updated is_staff status
                user = User.objects.get(pk=user.pk)
                print(f"Logged in user: {user.username}, is_staff: {user.is_staff}, session key: {request.session.session_key}")  # Debug log
                messages.success(request, "Login successful!")
                return redirect('index')
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email!")

    return render(request, 'register.html', {'form': form})


@login_required
def logout_view(request):
    # Explicitly flush the session to clear all session data
    request.session.flush()
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('register')


def index(request):
    template = loader.get_template('index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

from django.contrib.auth.decorators import login_required

@login_required
def participant(request):
    template = loader.get_template('participant.html')
    date_t = dt.datetime.now().date()
    time_t = dt.datetime.now().time()

    # Debug log user info
    print(f"User: {request.user}, is_staff: {request.user.is_staff}")

    # Sort the events getting displayed on Participants page sorted by earlier deadline first
    event_database = Event.objects.all().order_by('deadlineDate', 'fromDate', 'fromTime')
    e_data = []
    for e in event_database:
        if e.deadlineDate > date_t or e.deadlineDate == date_t and e.deadlineTime > time_t:
            e_data.append(e)
        else:
            continue
    context = {
        'events': e_data,
        'show_participant_registration': not request.user.is_staff,
    }

    # Collect data from Form and add it to database by creating an instance of participants
    if request.method == 'POST':
        participant_obj = Participant(
            name=request.POST['participantName'],
            cno=request.POST['cno'],
            email=request.user.email,
            event=request.POST['event'],
            regType=request.POST['regType'],
        )
        # Handle payment method fields
        payment_method = request.POST.get('paymentMethod', '')
        card_number = request.POST.get('cardNumber', '')
        expiry = request.POST.get('expiry', '')
        cvv = request.POST.get('cvv', '')
        upi_id = request.POST.get('upiId', '')
        bank_select = request.POST.get('bankSelect', '')

        # You can add logic here to save or process payment info as needed
        # For now, just print or log for debugging
        print(f"Payment Method: {payment_method}")
        print(f"Card Number: {card_number}")
        print(f"Expiry: {expiry}")
        print(f"CVV: {cvv}")
        print(f"UPI ID: {upi_id}")
        print(f"Bank Selected: {bank_select}")

        if participant_obj.regType == 'Individual':
            if request.POST['groupSize'] != '1':
                return error(request, 'Invalid Group size for Individual Registration.')        # redirect to error page via verifying groupSize for indiviual participants
            else:
                participant_obj.groupSize = request.POST['groupSize']
        else:
            participant_obj.groupSize = request.POST['groupSize']

        p_database = Participant.objects.all()
        for p in p_database:
            if participant_obj.email == p.email and participant_obj.event == p.event:       # Unique Email check
                error_msg = 'Email already registered for the selected event!'
                return error(request, error_msg)
            else:
                continue
        participant_obj.save()

        
        try:
            flask_api_url = 'http://localhost:5000/api/events/add'
            payload = {
                'participant_name': participant_obj.name,
                'participant_email': participant_obj.email,
                'event': participant_obj.event,
                'regType': participant_obj.regType,
                'groupSize': participant_obj.groupSize,
            }
            response = requests.post(flask_api_url, json=payload)
            if response.status_code == 200:
                print('Flask API event add notification successful.')
            else:
                print(f'Flask API event add notification failed with status code {response.status_code}.')
        except Exception as e:
            print(f'Error calling Flask API event add endpoint: {e}')

        # Twilio SMS Code
        # client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        # client.messages.create(
        #     body="\n\nThank you for participating in " + participant_obj.event + ".\n\nTickBird\nEventManager Web App",
        #     from_=settings.TWILIO_NUMBER,
        #     to=str(participant_obj.cno)
        # )
        return success(request, 'Registration Successful!!\nSMS has been send to the registered contact number.')           # redirect to success page
    return HttpResponse(template.render(context, request))

from django.contrib.auth.decorators import login_required

@login_required
def event(request):
    template = loader.get_template('event.html')


    if request.method == 'POST':
        e_obj = Event(
            eventName=request.POST['eventName'],
            description=request.POST['description'],
            location=request.POST['location'],
            fromDate=request.POST['fromDate'],
            fromTime=request.POST['fromTime'],
            toDate=request.POST['toDate'],
            toTime=request.POST['toTime'],
            deadlineDate=request.POST['deadlineDate'],
            deadlineTime=request.POST['deadlineTime'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        date_t = str(dt.datetime.now().date())
        time_t = str(dt.datetime.now().time())
        if date_t < e_obj.fromDate and date_t < e_obj.toDate and (
                date_t < e_obj.deadlineDate or (date_t == e_obj.deadlineDate and time_t < e_obj.deadlineTime)):
            if e_obj.toDate > e_obj.fromDate or (e_obj.toDate == e_obj.fromDate and e_obj.toTime > e_obj.fromTime):
                e_obj.save()

               
                subject = '[EVENTMANAGER] ' + e_obj.eventName + ' Registered Successfully!'
                content = 'Hello Host,\n\n' + 'The details of the event are as follows:\n\n' \
                          + 'Event ID - ' + str(e_obj.id) + '\n' \
                          + 'Description - ' + str(e_obj.description) + '\n' \
                          + 'Venue - ' + str(e_obj.location) + '\n' \
                          + 'Timeline - ' + 'From ' + str(e_obj.fromDate) + ', ' + str(e_obj.fromTime) + ' to ' + str(e_obj.toDate) + ', ' + str(e_obj.toTime) + '\n' \
                          + 'Registration Deadline - ' + str(e_obj.deadlineDate) + ', ' + str(e_obj.deadlineTime) + '\n' \
                          + 'Event Password - ' + str(e_obj.password) + '\n' \
                          + '\n\nThank you for using Event Manager.\n' \
                          + 'Regards,\nTickBird\nEventManager WEB APP'
                to = [e_obj.email]
                send_mail(
                    subject,                          # subject
                    content,                          # content
                    settings.EMAIL_HOST_USER,         # from
                    to,                               # to
                )
                return success(request, 'Email sent Successfully!!!')
            else:
                return error(request, 'End time less than Start time')
        else:
            return error(request, 'Invalid date and time of the event')
    context = {
        'show_event_registration': request.user.is_staff,
    }
    return HttpResponse(template.render(context, request))

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    template = loader.get_template('dashboard.html')
    authorized = False

    
    if request.method == 'POST':
        try:
            eventId = int(request.POST['eventId'])
        except ValueError:
            return error(request, 'Invalid Event ID')
        pwd = request.POST['password']
        mail = request.POST['email']
        event_database = Event.objects.all()
        for e_obj in event_database:
            if e_obj.id == eventId : 
                if e_obj.password == pwd and e_obj.email == mail:
                    authorized = True
                    e_name = e_obj.eventName
                    print(f"Dashboard: eventName from Event: '{e_name}'")
                    p_database = Participant.objects.all()
                    for p_obj in p_database:
                        print(f"Dashboard: participant event: '{p_obj.event}'")
                    p_data = Participant.objects.filter(event__iexact=e_name)
                    context = {
                        'participants': p_data, 
                        'valid': authorized,
                        'no_participants_message': 'No participants registered for this event.' if not p_data else '',
                    }
                    return HttpResponse(template.render(context, request)) 
                else:
                    return error(request, 'Incorrect Password!!')
        return error(request, 'Invalid Event ID')
    context = {
        'show_event_dashboard': request.user.is_staff,
    }
    return HttpResponse(template.render(context, request))

def error(request, error_msg):
    template = loader.get_template('error.html')
    context = {
        'messages': error_msg
    }
    return HttpResponse(template.render(context, request))

def success(request, success_msg):
    template = loader.get_template('success_updated_v3.html')
    context = {
        'messages': success_msg
    }
    return HttpResponse(template.render(context, request))

@login_required
def my_registrations(request):
    template = loader.get_template('my_registrations.html')
    user_email = request.user.email
    print(f"my_registrations: logged in user email: {user_email}")
    registrations = Participant.objects.filter(email=user_email)
    print(f"my_registrations: found registrations emails: {[r.email for r in registrations]}")
    context = {
        'registrations': registrations,
    }
    return HttpResponse(template.render(context, request))

@login_required
def cancel_registration(request, participant_id):
    user_email = request.user.email
    participant = get_object_or_404(Participant, id=participant_id, email=user_email)
    if request.method == 'POST':
        participant.delete()

       
        try:
            flask_api_url = 'http://localhost:5000/api/events/cancel'
            payload = {
                'participant_name': participant.name,
                'participant_email': participant.email,
                'event': participant.event,
                'regType': participant.regType,
                'groupSize': participant.groupSize,
            }
            response = requests.post(flask_api_url, json=payload)
            if response.status_code == 200:
                print('Flask API event cancel notification successful.')
            else:
                print(f'Flask API event cancel notification failed with status code {response.status_code}.')
        except Exception as e:
            print(f'Error calling Flask API event cancel endpoint: {e}')

        return redirect('my_registrations')
    template = loader.get_template('cancel_registration.html')
    context = {
        'participant': participant,
    }
    return HttpResponse(template.render(context, request))

def privacypolicy(request):
    template = loader.get_template('privacypolicy.html')
    context = {}
    return HttpResponse(template.render(context, request))

def contact(request):
    template = loader.get_template('contact.html')
    context = {}
    return HttpResponse(template.render(context, request))

def flightbook(request):
    template = loader.get_template('flightbook.html')
    context = {}
    return HttpResponse(template.render(context, request))
