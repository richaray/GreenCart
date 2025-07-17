# 🛍️ GreenCart – Eco Receipts for a Sustainable Future

GreenCart is a web-based application built for the **Walmart Sparkathon**, under the theme **"Retail with Purpose: Building a Sustainable and Responsible Future."** It allows users to upload shopping receipts, analyze the environmental impact of their purchases, and receive eco-friendly insights through intelligent analytics.

---

## 🌿 Key Features

- 📄 **Upload Shopping Receipts (PDFs)**  
  Extracts item names and details from uploaded bills.

- ♻️ **AI-Generated Eco Receipts**  
  Assigns eco-scores to each item using AI (Gemini model), based on sustainability factors.

- 📊 **Analytics Dashboard**  
  Visualizes:
  - Average eco-score over time
  - Top eco-friendly items
  - Low-scoring items
  - Total receipts uploaded

- 🕘 **View Receipt History**  
  Allows users to view all uploaded receipts and expand each for eco-receipt details.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, Tailwind CSS, JavaScript  
- **Backend**: Python, Flask  
- **Database**: MySQL  
- **AI Integration**: Gemini API for eco-scoring  
- **Others**: PDF parsing, RESTful APIs, Data visualization (charts)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/richaray/GreenCart.git
cd GreenCart
```

### 2. Create Virtual Environment and Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate  # On Linux/Mac

pip install -r requirements.txt
```

### 3. Set Up the Database

- Create a MySQL database named `greencart`.
- Run the SQL script:

```bash
mysql -u your_username -p greencart < init.sql
```

- Update your `.env` file with your DB credentials.
- Add config.py file 


### 4. Run the Application

```bash
python app.py
```

Visit: `http://127.0.0.1:5000` in your browser.

---

## 📂 Project Structure

```
GreenCart/
├── templates/          # HTML templates
├── uploads/            # Uploaded PDF receipts
├── app.py              # Flask application
├── config.py           # DB configurations
├── init.sql            # SQL to initialize database
├── requirements.txt    # Python dependencies
└── .env                # Environment variables (DB credentials)
```

---

## 📈 Sample Screenshots
<img width="1920" height="1080" alt="Screenshot (6)" src="https://github.com/user-attachments/assets/ec5bd93a-6e70-4e05-982f-921e1e4ec14d" />

<img width="1920" height="1080" alt="Screenshot (3)" src="https://github.com/user-attachments/assets/7ed55b10-263f-4d69-aebd-5e971c3178b4" />
<img width="1920" height="1080" alt="Screenshot (4)" src="https://github.com/user-attachments/assets/3f5818db-8ab0-4729-9da7-c32e2a77abe7" />
<img width="1920" height="1080" alt="Screenshot (5)" src="https://github.com/user-attachments/assets/51f525dd-9959-4391-b472-a27011144001" />




---

## 💡 Future Enhancements

- Suggest greener alternatives for low eco-score items
- User rewards system for sustainable shopping habits
- Category-wise eco impact analysis
- Mobile app version

---


## 📜 License

This project is licensed under the MIT License.
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)


---

## 🏆 Developed For

**Walmart Sparkathon 2025**  
Theme: *Retail with Purpose – Building a Sustainable and Responsible Future*

---

## ✨ Author

**Richa Ray** – [GitHub](https://github.com/richaray)
