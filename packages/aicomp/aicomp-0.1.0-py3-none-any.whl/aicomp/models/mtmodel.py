from transformers import PreTrainedModel, DistilBertModel, BertModel
from torch import nn

class MTModelDistilbert(PreTrainedModel):
    
    def __init__(self, config, num_category_labels, num_misconception_labels):
        super().__init__(config)
        self.distilbert = DistilBertModel(config)
        self.cat_head = nn.Linear(config.hidden_size, num_category_labels)
        self.misc_head = nn.Linear(config.hidden_size, num_misconception_labels)
    
    def forward(self, input_ids, attention_mask=None, category_label=None, misconception_label=None):
        h = self.distilbert(input_ids, attention_mask).last_hidden_state[:, 0]
        cat_logits = self.cat_head(h)
        misc_logits = self.misc_head(h)
        
        loss = None
        if category_label is not None:
            loss = nn.CrossEntropyLoss()(cat_logits, category_label) + nn.CrossEntropyLoss()(misc_logits, misconception_label)
        
        return {
            'loss': loss,
            'logits': cat_logits,
            'logits_misc': misc_logits
        }
    
class MTModelBert(PreTrainedModel):
    
    def __init__(self, config, num_category_labels, num_misconception_labels):
        super().__init__(config)
        self.bert = BertModel(config)
        self.cat_head = nn.Linear(config.hidden_size, num_category_labels)
        self.misc_head = nn.Linear(config.hidden_size, num_misconception_labels)
    
    def forward(self, input_ids, attention_mask=None, category_label=None, misconception_label=None):
        h = self.bert(input_ids, attention_mask).last_hidden_state[:, 0]
        cat_logits = self.cat_head(h)
        misc_logits = self.misc_head(h)
        
        loss = None
        if category_label is not None:
            loss = nn.CrossEntropyLoss()(cat_logits, category_label) + nn.CrossEntropyLoss()(misc_logits, misconception_label)
        
        return {
            'loss': loss,
            'logits': cat_logits,
            'logits_misc': misc_logits
        }