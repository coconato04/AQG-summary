import re
import numpy as np
import torch
from transformers import PegasusTokenizer, PegasusModel
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from collections import defaultdict

# Inisialisasi tokenizer dan model Pegasus
model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
pegasus_model = PegasusModel.from_pretrained(model_name)

def preprocess_text(text):
    # Langkah 1: Hapus semua jenis nomor list
    list_patterns = [
        r'^\s*\d+\.\d+\.\d+',      # Sublist seperti 1.1.1, 2.3.4
        r'^\s*\d+\.\d+\b',           # Sublist seperti 1.1, 2.1
        r'^\s*\d+\.\d+\.',         # Sublist seperti 1.1., 2.1.
        r'^\s*\d+\)',              # List dengan format 1), 2), ...
        r'^\s*\d+\.\s+',           # List dengan format 1., 2., ...
        r'^\s*\d+\s+',             # List dengan format angka tanpa simbol seperti 1 2 3
        r'^\s*\(\d+\)\s*',         # List angka dalam tanda kurung seperti (1), (2), (3)...
        r'^\s*[ivxlcdm]+\)',       # List angka Romawi kecil seperti i), ii), iii), iv)...
        r'^\s*[IVXLCDM]+\)',       # List angka Romawi besar seperti I), II), III)...
        r'^\s*[ivxlcdm]+\.',       # List angka Romawi kecil seperti i., ii., iii., iv....
        r'^\s*[IVXLCDM]+\.',       # List angka Romawi besar seperti I., II., III....
        r'^\s*[•\-*]\s+',          # List bullet dengan simbol seperti •, -, *
        r'^\s*[a-z]\.\s+',         # List huruf kecil diikuti titik seperti a., b., c., ...
        r'^\s*[A-Z]\.\s+',         # List huruf besar diikuti titik seperti A., B., C., ...
        r'^\s*[a-z]\)\s*',         # List huruf kecil seperti a), b), c), ...
        r'^\s*[A-Z]\)\s*',         # List huruf besar seperti A), B), C), ...
        r'^\s*\([a-z]\)\s*',       # List huruf kecil dalam tanda kurung seperti (a), (b), (c)...
        r'^\s*\([A-Z]\)\s*',       # List huruf besar dalam tanda kurung seperti (A), (B), (C)...
    ]
    combined_pattern = r'|'.join(list_patterns)
    text = re.sub(combined_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Langkah 2: Hapus caption gambar seperti "Gambar 2.1.", "Sumber:", dan URL dengan berbagai format
    caption_pattern = r'(Gambar\s*\d+\.\s*\d*\s*.*?(?=\n|$)|Sumber\s*:\s*.*?(?=\n|$)|Sumber:\s*.*?(?=\n|$)|https?://[^\s]+\.com\b|www\.[^\s]+\.com\b|[^\s]+\.com\b)'
    text = re.sub(caption_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    # Langkah 3: Hapus kalimat yang mengandung tanda
    question_exclamation_pattern = r'.*?[?!].*?(?=\n|\Z)'  # Regex untuk mendeteksi kalimat tanya atau seru
    symbol_pattern = r'([^\n]*\.\.{2,}.*?[\n]?)'           # Menghapus kalimat dengan titik berlebih di akhir
    dots_pattern = r'(\.\s*){2,}|([.]{2,}|[•\-_]{2,}|[.…]{2,})' # Pola baru untuk menghapus deretan titik berlebih
    text = re.sub(question_exclamation_pattern, '', text)
    text = re.sub(symbol_pattern, '', text)
    text = re.sub(dots_pattern, '', text)  # Hapus semua deretan titik berlebih
    
    # Langkah 4: Menghapus seluruh line break dan menjadikan teks justified
    text = re.sub(r'\n+', ' ', text)  # Menghapus seluruh line break dan menggantinya dengan spasi
    text = re.sub(r'\s+', ' ', text)  # Menghapus seluruh spasi berlebih dan tabs
    
    return text.strip()

def split_sentences(text):
    # Pisahkan teks menjadi kalimat berdasarkan tanda baca
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip() and re.search(r'[.!?]$', s.strip())]

def get_pegasus(sentence):
    tokens = tokenizer(sentence, return_tensors="pt", truncation=True, padding="longest")
    with torch.no_grad():
        encoder_outputs = pegasus_model.encoder(input_ids=tokens.input_ids, attention_mask=tokens.attention_mask)
        embeddings = encoder_outputs.last_hidden_state.mean(dim=1).squeeze()
    return embeddings

def sentence_similarity_matrix(sentences):
    """Menghitung matriks kesamaan kalimat menggunakan embedding Pegasus."""
    sentence_embeddings = [get_pegasus(sentence).numpy() for sentence in sentences]
    # Menggunakan cosine similarity untuk matriks similarity Pegasus
    pegasus_similarity_matrix = cosine_similarity(sentence_embeddings)
    
    # Membuat similarity matrix standar menggunakan cosine similarity langsung
    text_similarity_matrix = cosine_similarity(sentence_embeddings)  # Misal ini hasil dari TextRank juga (bisa diubah ke metode lain)
    
    # Menghitung final_similarity_matrix dengan formula yang Anda sebutkan
    final_similarity_matrix = np.multiply(pegasus_similarity_matrix, text_similarity_matrix)
    
    return final_similarity_matrix

# def textrank_summary(sentences, similarity_matrix, summary_ratio=1.0): #summary ratio disini dipakai untuk menentukan presentase teks asli yang akan mau dirangkum
#     nx_graph = nx.from_numpy_array(similarity_matrix)
#     scores = nx.pagerank(nx_graph)
#     mean_score = np.mean(list(scores.values()))
    
#     # Filter kalimat berdasarkan skor Textrank yang lebih dari rata-rata
#     summary_sentences = [sentence for i, sentence in enumerate(sentences) if scores[i] > mean_score]

#     # Tentukan jumlah kalimat yang akan diambil
#     num_sentences = max(1, int(len(sentences) * summary_ratio))
    
#     # Ambil kalimat sesuai dengan jumlah yang diinginkan tanpa indeks
#     summary_sentences = summary_sentences[:num_sentences]
    
#     # Gabungkan kalimat menjadi ringkasan
#     summary = ' '.join(summary_sentences)
#     return summary

def textrank_summary(sentences, similarity_matrix, summary_ratio=0.7):
    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    num_sentences = max(1, int(len(sentences) * summary_ratio))
    selected_sentences_with_index = sorted(ranked_sentences[:num_sentences], key=lambda x: sentences.index(x[1]))
    summary = ' '.join([s for _, s in selected_sentences_with_index])
    return summary

def extractive_summary(text, summary_ratio=0.7): 
    """Fungsi utama untuk menghasilkan ringkasan ekstraktif dari teks hasil scraping."""
    text = preprocess_text(text)  # Bersihkan teks sebelum memulai
    
    sentences = split_sentences(text)  # Pisahkan teks menjadi kalimat
    
    if len(sentences) == 0:
        return ""  
    
    similarity_matrix = sentence_similarity_matrix(sentences)  
    
    summary = textrank_summary(sentences, similarity_matrix, summary_ratio)  
    
    return summary


# # Contoh penggunaan dengan teks hasil scraping
# text = """"""

# # Menghasilkan ringkasan ekstraktif dengan pembobotan untuk teori
# summary = extractive_summary(text, summary_ratio=1.0, weighted=True)
# print("Ringkasan Ekstraktif:\n", summary)