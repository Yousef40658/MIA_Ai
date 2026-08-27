# MIA Slides — Embeddings, RNNs, and LSTMs

## Table of Contents
1. [Embeddings](#embeddings)
   - [Types of Embeddings](#types-of-embeddings)
   - [Approaches to Word Embeddings](#approaches-to-word-embeddings)
     - [Frequency-Based Approaches](#frequency-based-approaches)
   - [Similarity Measures](#similarity-measures)
   - [Sparse vs Dense Vectors](#sparse-vs-dense-vectors)
   - [Evaluation Metrics](#evaluation-metrics)
2. [Limitations of a Neural Network](#limitations-of-a-neural-network)
3. [RNNs (Recurrent Neural Networks)](#rnns-recurrent-neural-networks)
   - [Key Components of RNNs](#key-components-of-rnns)
   - [Types of Recurrent Neural Network](#types-of-recurrent-neural-network)
   - [Searching for Interpretable Cells](#searching-for-interpretable-cells)
   - [Advantages](#advantages)
   - [Disadvantages](#disadvantages)
4. [LSTMs (Long Short-Term Memory)](#lstms-long-short-term-memory)
   - [Main Idea](#main-idea)
   - [Strengths](#strengths)
   - [Issues](#issues)

---

## Embeddings

Since a neural network works with numbers, not text, we need to convert each word/token into vectors. But with some encodings, every word ends up mathematically unrelated to every other word.

An embedding maps each word/token to a relatively small, dense vector. Embeddings aren't set manually — the neural network learns these numbers during training.

I remember seeing in a 3Blue1Brown video that embeddings of related words end up "pointing" in the same direction along some dimensions.

While training, gradient descent adjusts those vectors until similar things end up pointing in the same direction, which leads to more accurate results. For example, "barking" and "dog" should end up pointing in the same direction along some dimensions, so the model can correctly complete a sentence like:

> "The dog is ... loudly" (just an example — I know it's not exactly like that)

Embeddings can also represent high-dimensional, complex data like images or audio — not just text.

Each embedding is a vector of, say, 128 dimensions. A 128-dimensional space isn't something a human can interpret directly, but it's understood by the RNN.

```
Words
  ↓
Token IDs
  ↓
Embedding
  ↓
Dense vectors
  ↓
RNN / LSTM
  ↓
Hidden representation
  ↓
Output
```

### Types of Embeddings

**1. Word Embeddings**
Represents each word with a dense vector (discussed above).

1. **Word2Vec** — learns word vectors based on their context; words appearing in similar contexts tend to get similar embeddings. Feels like this would be useful if you're building something related to a specific domain/topic.
2. **GloVe** — instead of primarily looking at individual prediction tasks like Word2Vec, GloVe uses global word co-occurrence statistics. For example, "cat" frequently occurs with "pet" and "milk"; "king" frequently occurs with "male" and "kingdom."
3. **FastText** — represents words using subwords, breaking them down instead of dealing with the complete word. Useful for rare words that are combinations of other words. Feels like this would be very useful with German, since most words there are combinations of multiple shorter words.

**2. Contextual Embeddings**
Traditional embeddings (above) give one vector per word regardless of context. The vector ends up agreeing with "the words that appear in all of its contexts" along some dimensions, but not fully.

Contextual embeddings provide multiple vectors per word, and depending on the context, the model uses the corresponding embedding.

Examples: ELMo, BERT, and GPT-style models.

**3. Sentence Embeddings**
Instead of embedding one word, an entire piece of text is embedded. Useful for semantic search (semantic search is a data-lookup method that understands the meaning and intent behind a user's words rather than looking for exact word matches — it uses context, synonyms, and concepts to find relevant information).

I remember using something similar in last year's training, with player information/spec embeddings.

**4. Image Embeddings**
Representing an image directly as a compact vector instead of millions of pixel values. Similar images end up with similar embeddings — useful for image-similarity tasks.

**5. Graph Embeddings**
Numbers that represent nodes in a graph, capturing node information and how nodes are connected/related.

### Approaches to Word Embeddings

#### Frequency-Based Approaches
Embeddings that concern themselves with how often a word appears, especially around the other words that give it context.

**1. Co-occurrence Matrix**
The matrix that contains all words in a text and the number of co-occurrences in the given data.

- Co-occurrence is used to build the vectors for each word — the words "cat" and "milk" seem to occur together often, so their embeddings should be related.

  ![alt text](image.png)

- As you can see in the image, the dot product (a measure of how aligned two vectors are) of "cat" and "dog" gives 20, while "milk" and "dog" give 10, and "cat" and "milk" give 10. "Car" with anything gives 0. So in the given data, cats and dogs are related ("both are animals"), and milk is what they drink (just an example on small data).

- One problem with the co-occurrence matrix is that it explodes as the number of words in the data increases, and most of the elements will be zero, since a word might realistically appear with — being generous — around 2000 other words, and the rest will be zeros.

**2. TF-IDF (Term Frequency–Inverse Document Frequency)**
- **Term Frequency** measures how often a word appears in a document.
- **Inverse Document Frequency** measures how rare a word is across the entire collection of documents. If a word like "the" appears in every document, it's not a special word — it gets a low IDF weight. A word like "electrospinning," which appears rarely, is more informative about the context.

**3. One-Hot Encoding**
- Gives each category a number. I encountered something similar in Task 3 with the position of the goalkeepers, but it was better to break the 4 positions into multiple columns rather than encode them as numbers, since 4 isn't a "higher" number — it's just a different position, so the model shouldn't learn "magnitude." I guess it would have been okay for a tree model, but even a tree model wouldn't mind the splitting into columns.
- **Dimensionality** — for something like nationality in Task 3, it's not realistic to add ~100 columns, because classical machine learning models end up overfitting, or fail to learn a correct structure with such a large number of features.
- **Sparse vectors** — with the nationality situation again, all rows will be 0 except for the correct nationality.
- **No semantic meaning** — all words are equally distant in the vector space; similar words are not close together. For example, a defender should be closer to a goalkeeper than to an attacker (kind of — I don't know football ._.).

**4. Bag of Words**
- Represents a document by which words it contains and how many times each word appears, ignoring word order. "I love cats" is the same as "cats love I."

  ![alt text](image-1.png)

- So it knows which words appear, but not who chased whom, which can make sentences less logical.
- Still suffers from high dimensionality, since vector_size = vocabulary_size, which can be very large and is mostly a zero vector — same problem: "a word won't be next to most other words."

### Similarity Measures

**1. Euclidean Distance**
The distance between two vectors. If one vector is larger than the other, it results in a large distance even if they're pointing in the same direction.

**2. Cosine Similarity**
Rather than relying on distance (and suffering from the Euclidean distance problem), it measures the angle between two vectors. The smaller the angle, the more the vectors "point in the same direction," and the more similar they are — useful with embeddings, since we've been saying all along that similar things point the same way.

It's a normalized dot product, since the dot product also measures alignment.

### Sparse vs Dense Vectors

**1. Sparse Vectors**
Vectors that result from the frequency-based methods discussed above, which are mostly zeros and, because of that, large in size.

**2. Dense Vectors (actual embeddings)**
Low-dimensional vectors, made mostly of information, learned through backpropagation.

### Evaluation Metrics

**1. Intrinsic Evaluation**

1. **Word Similarity**
2. **Word Analogy**
   As mentioned above, similar or related words end up pointing in the same direction. "Male" and "female" may "agree" on the same dimension (both are genders) but be opposite on another dimension (opposite types of gender).

   *king − man + woman ≈ queen.* Things like this tend to happen between embeddings — you can move from "king" to "queen" using logical operations: stripping the "male" component from "king," then adding the "female" component.

   "Tokyo" and "Japan" will be related, similarly to "Paris" and "France."

3. **Extrinsic Evaluation**
   Tests the accuracy of multiple embeddings to choose the one with the higher accuracy.

4. **Language Generation Metrics**

   **I. Perplexity**
   Measures how surprised/confident a model is. When evaluating the model, if it assigns high probability to the "correct" word, its perplexity is lower and it isn't surprised by being right or wrong. (I feel like this is similar to log loss, where confident mistakes are punished more.)

   **II. BLEU**
   Commonly used for evaluating generated text against one or more reference texts. BLEU checks how many n-grams overlap between the generated sentence and the reference.

   Suppose the reference is "The cat is sitting on the couch" and the model generates "The cat is sitting on the bed" — the sentences are fairly close, so BLEU looks at overlapping n-grams.

   BLEU considers overlaps of 1-, 2-, 3-, and 4-grams to judge the sentence, along with a brevity penalty (a penalty applied to incomplete sentences, penalizing candidates that are shorter than the reference). "The cat" alone shouldn't get a 2-gram match credit against the sentences above just because it's not close to them — it's incomplete.

   - **Unigram BLEU** — checks single words and ignores order; only checks whether the word exists in the reference.
   - **Bigram and higher BLEU** — checks pairs or groups of consecutive words, taking exact order into account.

   Example:
   - "The company announced a new product yesterday."
   - "Yesterday, the company announced its new product."

   These two sentences will score 1.0 on unigram BLEU, 0 on higher-order BLEU, and only 3 matches at the bigram level, even though both sentences mean the same thing.

   **III. ROUGE**
   ROUGE measures how much of the reference text is covered by the generated text — common for text summarization.

   ROUGE compares consecutive n-grams, just like BLEU. ROUGE-L is different because it uses the longest common subsequence rather than exact consecutive n-grams, to avoid the problem where BLEU misjudges sentences that carry the same meaning but in a different order.

   - **ROUGE-1** breaks text into single words and checks how many exist in the reference.
   - **ROUGE-2, ROUGE-3**, etc. are similar to BLEU.
   - **ROUGE-L** uses the longest common subsequence — how well the sequence and words are respected relative to the reference.

   Same example:
   - "The company announced a new product yesterday."
   - "Yesterday, the company announced its new product."

   A 5-gram subsequence — [the, company, announced, new, product] — appears in both (in the correct relative order, regardless of the words in between), showing a strong relationship between the two sentences and a strong indication that they're essentially the same sentence.

   **IV. METEOR**
   Compares generated text with a reference but doesn't constrain itself to exact word matches — it looks for semantic relationships between words that don't match completely.

   - "The cat plays."
   - "The kitten plays."

   BLEU and ROUGE would miss that "cat" and "kitten" are highly related. METEOR uses exact matches, stem matches, and synonym matches.

   METEOR penalizes wrong ordering similarly to BLEU, but applies a partial penalty rather than treating it as fully wrong the way BLEU does.

   Worth noting: METEOR uses lexical resources like WordNet instead of embeddings.

   ![alt text](image-4.png)

   **V. BERTScore**
   Similar to METEOR, but uses contextual embeddings to compare semantic similarity between generated and reference text.

   - "The automobile is fast."
   - "The car is very quick."

   These will get a high similarity score, since "automobile" ≈ "car" and "fast" ≈ "quick."

   **VI. Human Evaluation** — but that's ._.

**General Metrics**

![alt text](image-2.png)

---

## Limitations of a Neural Network

**1. No Memory**
Processes each data point independently — doesn't recognize that the order of data points matters.

"I couldn't complete the task because the task is ...." — if the model looks at the whole sentence, it's easy to suggest "hard" or "difficult," but if it only looks at "the task is ....," the completion is essentially random.

**2. Needs Fixed-Size Input**
When designing the input layer of a neural network, the size is already hardcoded — you can't increase or decrease it at runtime, because that would introduce untrained weights.

We could truncate input to a fixed length, but that comes with a loss of information.

**3. Doesn't Realize Order**
"The cat chased the dog" and "the dog chased the cat" are completely different in meaning, yet contain the same words. If you tokenize by word and look at one word at a time, both sentences produce the same processing in the neural network.

- "No, the food was good."
- "The food was no good."

---

## RNNs (Recurrent Neural Networks)
[Reference: GeeksforGeeks — Introduction to Recurrent Neural Network](https://www.geeksforgeeks.org/machine-learning/introduction-to-recurrent-neural-network/)

The fundamental problem RNNs try to solve: **how can a neural network process data where order matters?**

![alt text](image-5.png)

A recurrent neural network has a loop that passes information from the previous step to the current step, creating a memory of past inputs — like a sequential logic circuit.

### Key Components of RNNs

**1. Recurrent Neurons**
Hold a hidden state that carries information from the past to the next step.

![alt text](image-7.png)

**2. Hidden State (Memory)**

![alt text](image-8.png)
![alt text](image-9.png)

Suppose we have the sequential data x₁ → x₂ → x₃ → x₄.

- x₁ enters the RNN, resulting in hidden state h₁.
- h₁ and x₂ enter the RNN, resulting in h₂.
- h₂ and x₃ enter the RNN, resulting in h₃, and so on.

```
current input
     +
previous memory
     ↓
    RNN
     ↓
 new memory
```

`ht = f(xt, ht−1)`

![alt text](image-11.png)

So the current state h is built from the previous state, information about the current input, and the weights/biases. As you move forward, you're effectively carrying a running summary of the weights and biases applied to all previous inputs.

**3. Recurrent Neural Network Architecture**
The same RNN parameters are reused at every time step, so the previous inputs/hidden states remain meaningful for the next ones.

![alt text](image-13.png)
![alt text](image-14.png)

**4. Backpropagation Through Time (BPTT) in RNNs**
Since every h depends on the previous one, if the final prediction is wrong, the error can be traced back to a hidden state that was completely off (e.g., h5 out of 20 states). h20 depends on h19, h19 depends on h18, ... down to h2 depending on h1.

To visualize the process, we treat the RNN as multiple neural networks repeated across time rather than as a single loop (an RNN has the same weights at every time step).

In a normal 3-layer neural network, where dW3 is the weight of the output layer and dh3 is the output, the loss gradient is:

`dl/dW3 = dl/dh3 * dh3/dW3`

Since it's the same weights throughout in an RNN:

`dl/dw = dl/dh3 * dh3/dw`

— how much the loss changes as h3 changes, multiplied by how much h3 changes as the weight changes.

`dh3/dw`: how much h3 changes as the weight changes. h3 changes with the weight through two components, h1 and h2 — it's like a tree.

![alt text](image-15.png)

So the weights affect h3 through two paths: directly, and through h2. Represented by these equations:

![alt text](image-16.png)
![alt text](image-18.png)
![alt text](image-19.png)

### Types of Recurrent Neural Network

**1. One-to-One**
._. that's just a regular neural network — no sequential data.

![alt text](image-20.png)

**2. One-to-Many**

![alt text](image-22.png)

Processes a sequence of outputs from a single input (like an image) — the model generates a sequence, such as an image description.

It keeps passing the input and the extra information it found forward to build upon, until a stop token (a learned signal the model itself produces when it decides it can no longer learn anything else). So it learns something, keeps what it learned, then passes through the network again. I guess this is the same as effectively making the network longer, layer-wise.

![alt text](image-21.png)

**3. Many-to-One**

![alt text](image-23.png)

The type we've been discussing so far: sequential input producing one final output, using the final hidden state which contains the learned information needed to decide. Useful for things like sentiment analysis, where a piece of text feedback (a sequence of words) is turned into "positive" or "negative."

**4. Many-to-Many**

![alt text](image-24.png)

Each intermediate hidden state is used to produce an output. In the different-length many-to-many variant, it's not necessary for each hidden state to produce an output (output length ≠ input length).

**5. Sequence to Sequence**
Combines multiple RNN types, where the output of layer n matches the expected input of layer n+1.

![alt text](image-25.png)

### Searching for Interpretable Cells

We know each hidden state is a vector. An RNN can have, say, 200 hidden states/values describing its state across different timestamps.

**Cell**
A cell is a component of the state vector. By observing all the vectors, you can see how this component's value changes as the RNN learns new information — for example, if a cell represents how positive the input is.

![alt text](image-27.png)

Since we don't explicitly set the meaning of each cell, when looking at the whole hidden-state vector, we can still interpret something by observing it. I wouldn't be surprised if this corresponds to some explainable-AI method that tries to find correlation/information by tracking how a cell progresses.

*"Is there a particular neuron whose activation strongly correlates with some recognizable concept?"*

Information can be distributed across many neurons — a group of neurons can move in an explainable way as it learns a certain type of information.

**Examples of Cells**

1. **Quote Detection Cell** — a cell that corresponds to the text being inside quotation marks.
2. **Line Length Tracking Cell** — a cell that may correspond to indentation before words, useful for things like Python scripts.
3. **If-Statement Cell** — a cell that may correspond to being inside blocks like `if` or `while` in C-like languages.

### Advantages

1. **Processes any length of input** — since you can use one-to-many, many-to-one, etc. with sequential data. The model size doesn't increase for longer inputs — just more tokenizing is done.
2. **Uses information from many steps back.**
3. **Symmetrical** — the same weights are applied at every timestep. While this is a requirement, it's still an advantage, since it heavily reduces the number of parameters that need to be tuned.
4. **Enhanced pixel neighborhoods** — RNNs can be combined with convolutional layers to capture extended pixel neighborhoods, improving performance on image and video data.

### Disadvantages

1. **Slow** — recurrent computation is inherently sequential, so it can't be parallelized on a GPU.
2. **Difficulty accessing information from many steps back** — in practice.
3. **Vanishing Gradient**
   As stated in the equation above:

   ![alt text](image-18.png)

   Components with multiple multiplications (like the third term) end up very small if even one of the gradients involved is very small, or if all of them are fractions.

   So assume you have 100 steps — steps after, say, step 20 aren't really contributing to the weight updates, since they're multiplied by everything above them, and if those are small, the product is essentially 0.

   If the weight update is almost nothing, the model "decides" it has learned, even if it hasn't yet — or because the update is flawed due to earlier hidden states that can't "say" they need their weights updated.

   ![alt text](image-28.png)

4. **Exploding Gradients**
   Same problem as vanishing gradients, but occurs when the values are greater than 1 — when multiplied together, the weights end up updating too aggressively.

---

## LSTMs (Long Short-Term Memory)
[Reference: GeeksforGeeks — Introduction to Long Short-Term Memory](https://www.geeksforgeeks.org/deep-learning/deep-learning-introduction-to-long-short-term-memory/)

Introduced to solve the vanishing gradient problem, where the network struggles to preserve important earlier information as time progresses.

### Main Idea

Instead of having one hidden state, an LSTM has two states:
- **hₜ** — hidden state
- **Cₜ** — cell state

The cell state is connected across time steps through three gates that let the network decide whether to keep, forget, or add new information. Each gate produces a value between 0 and 1, usually via the sigmoid function — so it's not a binary switch, it's a soft gate.

![alt text](image-29.png)

**1. Forget Gate**
Decides what old information to remove, using the current input and previous hidden state to determine how relevant the previous information is to the current input.

![alt text](image-30.png)

- `Wf` represents a learned weight matrix.
- `[ht-1, xt]` represents the concatenation of the current input and previous hidden state.
- `Wf · [ht-1, xt]` is the same as `Wfh · ht-1 + Wfx · xt`.

So the matrices are also effectively concatenated, and since it's one row and one column, it's basically the same operation. Since Wf is a learnable matrix, it doesn't have a forced behavior, but realistically — I think — it ends up removing memory when the input is irrelevant to old memory, e.g., when a new topic starts and old memories are no longer needed.

**2. Input Gate**
Decides how much of the new information should be written to the cell state, using another learnable matrix.

![alt text](image-32.png)

`C̃t` is the list of candidates. The input gate decides how much of each candidate value should actually be stored, acting as a filter. `Ct` is the resulting long-term memory.

For example:

```
candidate:
C̃t = [0.7, 0.9, -0.4, 0.6, 0.2]

input gate:
it = [0.1, 0.8, 0.3, 0.95, 0.05]

result:
[0.1 × 0.7, 0.8 × 0.9, 0.3 × -0.4, 0.95 × 0.6, 0.05 × 0.2]
 = [0.07, 0.72, -0.12, 0.57, 0.01]
```

![alt text](image-33.png)

So the candidate list contains information that may be useful, and it's then evaluated by the input gate to decide which information really matters enough to be added to the cell state.

![alt text](image-34.png)
![alt text](image-35.png)

**3. Output Gate**
Determines which information from the current cell state should be passed on as the hidden state (output) at the current time step, using the current input and previous hidden state.

![alt text](image-36.png)
![alt text](image-37.png)

```
                    ┌── Forget ──→ remove old information
                    │
Previous memory ────┼── Keep ─────→ preserve information
                    │
Current input ──────┼── Add ──────→ store new information
                    │
                    └── Output ───→ expose information
```

### Strengths

- Almost always outperforms vanilla RNNs by avoiding the vanishing gradient problem.
- Captures long-range dependencies well — since (logically, not mathematically) only important information is kept, the model can focus on it more easily, while useless/irrelevant information is forgotten rather than kept around.

### Issues

- More weights — every gate has at least two learned matrices.
- Because of more weights, more data is needed to train the model and avoid underfitting.
- Can still suffer from vanishing/exploding gradients.
- Slow — due to the increased number of parameters, and the process is still sequential. Expect roughly 2–3x the original time, given the number of added matrices and calculations.

---

### Types of RNNs
seems logical, elsra7a ._.