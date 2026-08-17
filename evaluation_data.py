from __future__ import annotations

from typing import Dict, List

QUESTION_SET: List[Dict[str, str]] = [
    {
        "question_id": "Q001",
        "channel": "USSD",
        "question_text": "A 32-year-old woman reports fever, cough, and mild chest pain for 2 days. She is otherwise stable. What is the most appropriate first step?",
        "clinical_reference": "Assess for red flags and arrange a clinical evaluation; if symptoms are worsening or she has breathing difficulty, seek urgent medical assessment. Supportive care and monitoring are appropriate while considering differential diagnoses such as respiratory infection.",
        "feature_type": "symptom_triage",
    },
    {
        "question_id": "Q002",
        "channel": "USSD",
        "question_text": "A patient with diabetes says they missed two doses of metformin and feels dizzy after skipping meals. What should they do?",
        "clinical_reference": "Check blood sugar if possible, eat a small carbohydrate snack, and contact a clinician or local nurse hotline if symptoms worsen. Do not double up on missed doses without guidance. Seek urgent assessment for severe weakness, confusion, or inability to keep fluids down.",
        "feature_type": "medication_guidance",
    },
    {
        "question_id": "Q003",
        "channel": "USSD",
        "question_text": "A patient needs a follow-up appointment for prenatal care but cannot travel to the clinic. Which route should the system suggest?",
        "clinical_reference": "Route the patient to a community or telehealth follow-up booking path and confirm the nearest facility with the appropriate obstetric service. If there are acute symptoms or danger signs, escalate to urgent care.",
        "feature_type": "appointment_routing",
    },
    {
        "question_id": "Q004",
        "channel": "USSD",
        "question_text": "A child has a mild fever and runny nose for 3 days without breathing problems. How should the triage engine respond?",
        "clinical_reference": "Provide home care advice and monitor hydration, fever, and respiratory status. Advise prompt assessment if the child develops difficulty breathing, lethargy, dehydration, or persistent high fever.",
        "feature_type": "symptom_triage",
    },
    {
        "question_id": "Q005",
        "channel": "USSD",
        "question_text": "A patient asks whether it is safe to take ibuprofen after a meal after strenuous exercise. What guidance is safest?",
        "clinical_reference": "Ibuprofen can be taken with food if appropriate for the patient, but dosing should follow package guidance and clinician advice, especially if they have kidney disease, ulcers, asthma, or are on blood thinners. Avoid assuming it is safe without checking contraindications.",
        "feature_type": "medication_guidance",
    },
    {
        "question_id": "Q006",
        "channel": "Mobile App",
        "question_text": "A user reports severe abdominal pain, vomiting, and fever for 12 hours. What tier of escalation is appropriate?",
        "clinical_reference": "This pattern warrants urgent assessment. The system should advise the user to contact emergency services or a clinician immediately, especially if pain is persistent or accompanied by fainting, blood in stool, or severe weakness.",
        "feature_type": "symptom_triage",
    },
    {
        "question_id": "Q007",
        "channel": "Mobile App",
        "question_text": "A patient has been prescribed amoxicillin and asks how to take it correctly with food. What is the correct guidance?",
        "clinical_reference": "Amoxicillin is typically taken as directed by the prescriber, often with or after food to reduce stomach upset. Complete the full course unless told otherwise and seek advice for missed doses or severe allergy symptoms.",
        "feature_type": "medication_guidance",
    },
    {
        "question_id": "Q008",
        "channel": "Mobile App",
        "question_text": "A patient wants to schedule a cardiology review after recurring chest discomfort. Which route is appropriate?",
        "clinical_reference": "Direct the patient to specialist referral or appointment booking with a cardiology service and note any urgent red flags such as chest pain with sweating, shortness of breath, or fainting. Same-day evaluation may be required if symptoms are acute.",
        "feature_type": "appointment_routing",
    },
    {
        "question_id": "Q009",
        "channel": "Mobile App",
        "question_text": "A user has a mild rash after using a new soap. What is the best safe response?",
        "clinical_reference": "Suggest stopping exposure to the irritant, washing the area gently, and seeking advice if the rash spreads, is painful, or the patient has facial swelling, wheezing, or breathing difficulty. A clinician should assess severe or worsening symptoms.",
        "feature_type": "symptom_triage",
    },
    {
        "question_id": "Q010",
        "channel": "Mobile App",
        "question_text": "A patient asks if they can use an antihistamine and a cold medicine together. What is the safest clinical answer?",
        "clinical_reference": "Do not recommend combinations without checking ingredients and contraindications. Many over-the-counter formulations contain overlapping active substances, so advise reviewing labels and consulting a pharmacist or clinician before combining medicines.",
        "feature_type": "medication_guidance",
    },
    {
        "question_id": "Q011",
        "channel": "Web Portal",
        "question_text": "A patient has severe shortness of breath, chest pain, and confusion. What is the recommended pathway?",
        "clinical_reference": "Escalate to emergency services immediately. This is a high-risk clinical condition requiring urgent medical care. Do not provide home treatment advice or delay assessment.",
        "feature_type": "symptom_triage",
    },
    {
        "question_id": "Q012",
        "channel": "Web Portal",
        "question_text": "A patient is taking blood pressure medication and asks what to do when they miss one dose. What is the safest guidance?",
        "clinical_reference": "Do not double the dose. Follow dose instructions, take the missed dose when remembered unless close to the next dose, and contact a clinician if there is dizziness, fainting, or concerns about blood pressure control. This should be framed as general information rather than prescriptive medical direction.",
        "feature_type": "medication_guidance",
    },
    {
        "question_id": "Q013",
        "channel": "Web Portal",
        "question_text": "A patient requests a referral for dermatology because of a recurring skin lesion. Which route should the system propose?",
        "clinical_reference": "Route the patient to specialist booking for dermatology evaluation. If the lesion is changing rapidly, painful, bleeding, or associated with systemic symptoms, prioritize urgent review.",
        "feature_type": "appointment_routing",
    },
    {
        "question_id": "Q014",
        "channel": "Web Portal",
        "question_text": "A person reports mild sore throat and fatigue but no difficulty breathing. What is appropriate self-care guidance?",
        "clinical_reference": "Recommend hydration, rest, and symptom monitoring. Advise urgent review if swallowing becomes difficult, breathing is affected, or the patient develops high fever or severe weakness.",
        "feature_type": "symptom_triage",
    },
    {
        "question_id": "Q015",
        "channel": "Web Portal",
        "question_text": "A patient has a prescription for oral contraceptives and asks if they can take them with antibiotics. What is the safest answer?",
        "clinical_reference": "General guidance should note that some antibiotics may affect contraceptive efficacy and that users should confirm with a clinician or pharmacist. Avoid definitive claims without checking the specific medication and local guidance.",
        "feature_type": "medication_guidance",
    },
]


FEATURE_TYPES = sorted({item["feature_type"] for item in QUESTION_SET})
CHANNELS = sorted({item["channel"] for item in QUESTION_SET})
