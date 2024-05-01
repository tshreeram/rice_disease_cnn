import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import re

from flask import redirect, render_template, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def is_valid_username(username):
    # Customize this function as needed
    return len(username) >= 4 

# Define password validation functions
def is_valid_length(password):
    return len(password) >= 8

def has_special_characters(password):
    return bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

def has_numbers(password):
    return any(char.isdigit() for char in password)

cause_symptom_remedies = {
    'bacterial leaf blight': {
        'causes': 'Caused by the bacterium Xanthomonas oryzae.',
        'symptoms': 'Water-soaked lesions on leaves, which later turn brown and elongated.',
        'remedies': 'Use copper-based fungicides such as Kocide, Serenade, or Actigard.'
    },
    'brown spot': {
        'causes': 'Fungal disease caused by Cochliobolus miyabeanus.',
        'symptoms': 'Small, oval to spindle-shaped, brown spots with yellow halos on leaves.',
        'remedies': 'Apply fungicides containing azoxystrobin, propiconazole, or tricyclazole.'
    },
    'healthy': {
        'causes': 'Healthy plant without any disease symptoms.',
        'symptoms': 'No visible symptoms present.',
        'remedies': 'Maintain proper plant nutrition and environmental conditions.'
    },
    'leaf blast': {
        'causes': 'Fungal disease caused by Pyricularia oryzae.',
        'symptoms': 'Elliptical or spindle-shaped lesions on leaves, stems, and panicles.',
        'remedies': 'Apply fungicides such as Tricyclazole, Propiconazole, or Azoxystrobin.'
    },
    'leaf scald': {
        'causes': 'Bacterial disease caused by Rhodococcus fascians or fungal infection caused by Rhynchosporium oryzae.',
        'symptoms': 'Long, narrow, brown to reddish-brown lesions on leaves.',
        'remedies': 'Use copper-based fungicides or bactericides like Kocide, Cuprofix, or Bordeaux mixture.'
    },
    'narrow brown spot': {
        'causes': 'Fungal disease caused by Cercospora oryzae.',
        'symptoms': 'Narrow, dark brown to black spots on leaves.',
        'remedies': 'Apply fungicides containing azoxystrobin, propiconazole, or tricyclazole.'
    },
    'neck blast': {
        'causes': 'Fungal disease caused by Magnaporthe grisea.',
        'symptoms': 'Gray to brown lesions near the leaf collar or neck of the rice plant.',
        'remedies': 'Apply fungicides such as Tricyclazole, Propiconazole, or Azoxystrobin.'
    },
    'rice hispa': {
        'causes': 'Insect pest, commonly known as the rice hispa (Dicladispa armigera).',
        'symptoms': 'Feeding damage by adults and larvae causes white or transparent streaks on leaves known as hopper burn.',
        'remedies': 'Use insecticides like Chlorpyrifos, Thiamethoxam, or Imidacloprid to control infestations.'
    },
    'sheath blight': {
        'causes': 'Fungal disease caused by Rhizoctonia solani.',
        'symptoms': 'White, water-soaked lesions on leaf sheaths that expand and turn brown.',
        'remedies': 'Apply fungicides such as Tricyclazole, Propiconazole, or Azoxystrobin.'
    },
    'tungro': {
        'causes': 'Viral disease caused by a complex of Rice tungro bacilliform virus (RTBV) and Rice tungro spherical virus (RTSV), transmitted by the green leafhopper Nephotettix virescens.',
        'symptoms': 'Stunted growth, yellowing and drying of leaves, and reduced tillering.',
        'remedies': 'Plant resistant varieties, control leafhopper populations using insecticides like Imidacloprid or Thiamethoxam.'
    }
}

def get_disease_info(prediction):

    return cause_symptom_remedies[prediction]
