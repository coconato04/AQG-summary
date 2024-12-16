import random
import spacy
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
from nltk.tokenize import sent_tokenize

# Load Spacy model for NER
nlp = spacy.load('en_core_web_trf')

# Initialize MT5 model
tokenizer = T5Tokenizer.from_pretrained('t5-base')
t5_model = T5ForConditionalGeneration.from_pretrained('t5-base')  # Tidak ada pengaturan device, default ke CPU

# Load template and labeled entity files
TEMPLATE_FILE_PATH = 'Generator/assets/data/template_soal_label.xlsx'
LABELED_ENTITIES_FILE_PATH = 'Generator/assets/data/labeled_entities.xlsx'

def load_additional_entities():
    xls = pd.ExcelFile(LABELED_ENTITIES_FILE_PATH)
    labeled_entities = {}
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        entities = df.values.flatten()
        labeled_entities.update({entity: sheet_name for entity in entities if pd.notna(entity)})
    return labeled_entities

def analyze_text_with_labeled_entities(text, labeled_entities):
    sentences = sent_tokenize(text)
    all_entities = []
    for sentence in sentences:
        doc = nlp(sentence)
        entities = [(ent.text, labeled_entities.get(ent.text, ent.label_)) for ent in doc.ents]
        all_entities.append(entities)
    return all_entities

def enrich_entities(entities, labeled_entities):
    enriched_entities = []
    for entity_list in entities:
        enriched_entity_list = []
        for ent_text, ent_label in entity_list:
            enriched_entity_list.append((ent_text, labeled_entities.get(ent_text, ent_label)))
        enriched_entities.append(enriched_entity_list)
    return enriched_entities

def load_templates_from_excel(question_type):
    sheet_name = 'isian' if question_type == 'isian' else 'PG'
    df = pd.read_excel(TEMPLATE_FILE_PATH, sheet_name=sheet_name)
    templates = df.iloc[:, 0].tolist()
    return templates

def match_templates(entities, templates):
    matched_questions = []
    for template in templates:
        matched_template = template
        for entity_list in entities:
            for ent_text, ent_label in entity_list:
                if f'[{ent_label}]' in matched_template:
                    matched_template = matched_template.replace(f'[{ent_label}]', ent_text)
        if '[' not in matched_template:
            matched_questions.append(matched_template)
    return matched_questions

def select_questions(matched_questions, num_questions):
    return random.sample(matched_questions, min(num_questions, len(matched_questions)))

def generate_answer(teks_konteks, soal, max_length=100):
    input_text = f"Jawab singkat: {soal} Konteks: {teks_konteks}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=512)
    
    # Model secara default akan berjalan di CPU jika tidak ada pengaturan CUDA
    output_ids = t5_model.generate(
        input_ids,
        max_length=max_length,  # Bisa disesuaikan untuk jawaban panjang atau pendek
        num_beams=5,
        early_stopping=True
    )
    jawaban = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return jawaban

def validate_answer(answer):
    return bool(answer and len(answer.split()) > 3 and answer.lower() not in ["no answer", "none", "irrelevant"])

def generate_questions_and_answers(materi, questions, num_questions, question_type, labeled_entities):
    context_based_qna = []
    for question in questions:
        if len(context_based_qna) >= num_questions:
            break

        answer = generate_answer(materi, question)
        if validate_answer(answer):
            if question_type == "isian":
                context_based_qna.append({'question': question, 'answer': answer})
            elif question_type == "PG":
                # Cari label yang diperlukan dari soal
                required_label = None
                for label in labeled_entities.values():
                    if f'[{label}]' in question:
                        required_label = label
                        break
                
                # Ambil entitas acak dari labeled_entities berdasarkan label yang cocok
                valid_entities = [ent for ent, label in labeled_entities.items() if label == required_label]
                if valid_entities:
                    ner_choice = random.choice(valid_entities)
                else:
                    ner_choice = "Pilihan tidak tersedia"

                # Buat pilihan jawaban
                choices = ["Semua Salah", answer, "Semua Benar", ner_choice]

                # Acak posisi jawaban
                random.shuffle(choices)

                context_based_qna.append({
                    'question': question,
                    'choices': {
                        'A': choices[0],
                        'B': choices[1],
                        'C': choices[2],
                        'D': choices[3]
                    },
                    'answer': answer  # Pastikan jawaban benar ditandai untuk validasi
                })

    return context_based_qna