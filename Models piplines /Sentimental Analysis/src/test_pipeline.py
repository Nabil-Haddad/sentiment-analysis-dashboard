from inference import aspect_based_sentiment
import time
import pandas as pd

test_comments = [
    # Straightforward + known aspect
    "The design is beautiful.",
    "The price is too expensive.",
    
    # Straightforward + known aspect + double aspect
    "The staff and service are nice.",

    # Straightforward + no known aspect
    "I really loved it.",
    "This was a complete waste of time.",

    # Positive then negative, both with known aspects
    "The design is beautiful but the performance is terrible.",
    "The staff were friendly but the service was very slow.",

    # Negative then positive, both with known aspects
    "The price is high but the quality is excellent.",
    "The performance was bad at first but the service was great.",

    # Complex: one part has aspect, one part has no aspect
    "The design is amazing but I still regret buying it.",
    "I hated the experience at first but the staff were very kind.",

    # Multiple aspects in one sentence part
    "The design and performance are both excellent.",
    "The price and delivery were disappointing.",

    # No aspect at all, mixed sentiment
    "I liked it at first but it became disappointing later.",
    "At the beginning it was confusing but in the end it was useful.",

    # Edge cases
    "The product is okay.",
    "Not bad, but not amazing either.",
    "The service was not terrible, but it was not great.",
    "The delivery was fast however the package looked damaged.",
]

start_time = time.perf_counter()

results = aspect_based_sentiment(test_comments)

end_time = time.perf_counter()

df_aspect = pd.DataFrame(results["with_aspects"])
df_without_aspect = pd.DataFrame(results["without_aspects"])

print(df_aspect.head(10))
print(10 * "#")
print(df_without_aspect.head(10))
print(f"This batch function took {end_time - start_time} s to be executed")