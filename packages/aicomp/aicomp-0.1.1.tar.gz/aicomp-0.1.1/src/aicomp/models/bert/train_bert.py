"""
Minimal BERT Training Script for Colab
- Expects dataset.csv with columns: QuestionId, QuestionText, MC_Answer, StudentExplanation, Category, Misconception
"""
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

df = pd.read_csv('dataset.csv')
df['Misconception'] = df['Misconception'].fillna('NA')
df['target_text'] = df['Category'].astype(str) + ':' + df['Misconception'].astype(str)
labels = sorted(df['target_text'].unique())
label2id = {l: i for i, l in enumerate(labels)}
df['label'] = df['target_text'].map(label2id)
train_df, val_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df['label'])

model_name = 'bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(labels))

def tokenize(batch):
    return tokenizer(batch['QuestionText'] + ' ' + batch['StudentExplanation'], truncation=True, padding='max_length', max_length=128)

import datasets
train_ds = datasets.Dataset.from_pandas(train_df)
val_ds = datasets.Dataset.from_pandas(val_df)
train_ds = train_ds.map(tokenize, batched=True)
val_ds = val_ds.map(tokenize, batched=True)

args = TrainingArguments(
    output_dir='./bert_model',
    evaluation_strategy='epoch',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    logging_dir='./logs',
    logging_steps=100,
)
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    tokenizer=tokenizer,
)
trainer.train()
