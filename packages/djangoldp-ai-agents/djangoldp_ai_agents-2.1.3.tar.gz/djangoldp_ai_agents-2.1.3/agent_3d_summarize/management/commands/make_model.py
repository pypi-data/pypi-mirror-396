import json
import os
from os import putenv

import pandas as pd
from datasets import Dataset
from django.core.management.base import BaseCommand
from transformers import (DataCollatorForSeq2Seq, T5ForConditionalGeneration,
                          T5Tokenizer, Trainer, TrainingArguments)

from agent_3d_summarize.helpers import json_to_prompt


class Command(BaseCommand):
    help = "Trains and saves the T5 3D summarizer model."

    def handle(self, *args, **options):
        putenv("HIP_VISIBLE_DEVICES", "0,1,2")

        base_path = os.path.join(os.path.dirname(__file__), "..", "..")

        # Convert dataset into Hugging Face dataset
        df = pd.read_csv(os.path.join(base_path, "dataset.csv"))
        dataset = Dataset.from_pandas(df)

        # Load model and Tokenizer
        model_name = "t5-small"
        tokenizer = T5Tokenizer.from_pretrained(model_name, revision="main")
        model = T5ForConditionalGeneration.from_pretrained(model_name, revision="main")

        # Tokenize dataset
        def preprocess(example):
            inputs = tokenizer(
                json_to_prompt(json.loads(example["input_text"])),
                max_length=512,
                padding="max_length",
                truncation=True,
            )
            targets = tokenizer(
                example["target_text"],
                max_length=150,
                padding="max_length",
                truncation=True,
            )
            inputs["labels"] = targets["input_ids"]
            return inputs

        tokenized_dataset = dataset.map(preprocess, batched=False)

        model_output_dir = "agent_3d_summarize/model"
        training_args = TrainingArguments(
            output_dir=model_output_dir,
            per_device_train_batch_size=4,
            learning_rate=3e-4,
            num_train_epochs=5,
            weight_decay=0.01,
            save_strategy="epoch",
            logging_dir="./logs",
            eval_strategy="no",
            fp16=True,  # si tu as un GPU compatible
        )

        # Helper that prepares data, notably adding the padding
        data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
        )
        trainer.train()

        # Save the model
        model.save_pretrained(model_output_dir)
        tokenizer.save_pretrained(model_output_dir)

        self.stdout.write(
            self.style.SUCCESS("Successfully trained and saved the model.")
        )
