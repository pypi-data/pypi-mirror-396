# ICDR
Contrastive Data Retrieval with Inverted Indexes

Efficient Approximate/Precise retrieval of similar documents for fine-tuning language models. The library can be used to quickly create contrastive pairs/triplets from large document collections. 

ICDR builds an inverted index structure and several fast look-up tables with the aim of retrieving similar texts from a corpus. The library is ideal for efficient entity matching, entity resolution, record linkage, and deduplication applications in the NLP realm. ICDR allows for very fast retrieval of similar, positive (i.e. matching), and negative (i.e. non-matching) text samples which can be used either directly, or to fine-tune LLMs and other models.