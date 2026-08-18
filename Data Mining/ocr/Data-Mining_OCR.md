# Data Mining (CT 725 02 / CT72502) — Full OCR Archive

Source scan: `D:\College\PYQ\Data Mining\Data-Mining.pdf` (26 pages, pure image scan —
`page.get_text()` returns EMPTY on every page).

Transcribed **verbatim** on 2026-08-11, including the papers' own typos
(`Spal_Width`, `Petal_Lenth`, `Labal`, `Baiyesian`, `anamoly`, `Transcation`,
`Predicated`, `Positve`, `COFIDENCE`, `dimentionality`, `spriori`, `defection`,
`Anomy`, `Material Status`, `FG- Growth`, `curve of Dimensionality`).
Do **not** silently correct them — the .tex documents quote these statements.

Every paper is **BE, IV/I, Full Marks 80, Pass Marks 32, Time 3 hrs**, programme
**BEX, BCT** (a single common paper — there is no separate BEI stream for this
subject, so the documents use bold/plain only and never `\texttt{}`).

---

## PAGE-ORDER TABLE

| PDF page(s) | Year / Month | Exam    | Programme | Subject line                              |
|-------------|--------------|---------|-----------|-------------------------------------------|
| p1–p2       | 2080 Bhadra  | Regular | BEX, BCT  | Data mining (CT72502) (Elective I)        |
| p3          | 2081 Baishakh| Back    | BEX, BCT  | Data Mining (CT72502) (Elective I)        |
| p4          | —            | —       | —         | **BLANK PAGE**                            |
| p5–p6       | 2080 Baishakh| Back    | BCT, BEX  | Data Mining (CT72502) (Elective-I)        |
| p7–p8       | 2079 Bhadra  | Regular | BEX, BCT  | Data Mining (Elective I)(CT72502)         |
| p9–p10      | 2078 Bhadra  | Regular | BEX, BCT  | Data Mining (Elective I)(CT 72502)        |
| p11–p14     | 2076 Chaitra | Regular | BEX, BCT  | Data Mining (Elective I) (CT72502)        |
| p15         | 2076 Ashwin  | Back    | BEX, BCT  | Data Mining (Elective I) (CT72502)        |
| p16         | 2075 Chaitra | Regular / Back | BEX, BCT | Data Mining (Elective I) (CT72502)  |
| p17         | 2075 Ashwin  | Back    | BCT, BEX  | Data Mining (Elective I) (CT72502)        |
| p18         | 2074 Chaitra | Regular | BEX, BCT  | Data Mining (Elective I) (CT72502)        |
| p19–p20     | 2074 Ashwin  | Back    | BEX, BCT  | Data Mining (Elective I) (CT72502)        |
| p21         | 2073 Shrawan | New Back (2066 & Later Batch) | BE, BCT | Data Mining (Elective II) (CT72502) |
| p22         | 2072 Chaitra | Regular | BEX, BCT  | Data Mining (Elective II) (CT72502)       |
| p23         | 2071 Chaitra | Regular | BEX / BCT | Data Mining (Elective I) (CT72502)        |
| p24         | 2072 Kartik  | New Back (2066 & Later Batch) | BEX, BCT | Data Mining (Elective I) (CT72502) |
| p25         | 2071 Shawan  | New Back (2066 & Later Batch) | BEX, BCT | Data Mining (CT72502) (Elective I) |
| p26         | 2070 Chaitra | Regular | BEX, BCT  | Data Mining (Elective I) (CT725)          |

**17 papers total.** Note the scan is NOT in strict year order: 2071 Chaitra (p23)
sits between 2072 Chaitra (p22) and 2072 Kartik (p24).
Years absent from the compilation: 2077 (no exam held), 2073 Chaitra,
2070 Ashwin, 2069.

Every paper carries the same four rubric lines, so they are not repeated below:

> ✓ Candidates are required to give their answers in their own words as far as practicable.
> ✓ Attempt **All** questions.
> ✓ The figures in the margin indicate **Full Marks**. *(2071 Chaitra and 2071 Shawan
>   instead read: ✓ **All** questions carry equal marks.)*
> ✓ Assume suitable data if necessary.

---

## p1–p2 — 2080 Bhadra, Regular, BEX/BCT, CT72502 (Elective I)

1. a) Write key features of data warehouse. Explain each steps of knowledge discovery data mining process with a suitable example. **[2+5]**

   b) How do similarity / dissimilarity is calculated? Find the cosine similarity between Object-2 and 4. Also calculate the Euclidean distance between object 1, 3 and object 1, 4. **[3+3+3]**

   | Object | Size | Weight | Color_Code | Taste_Score |
   |--------|------|--------|------------|-------------|
   | 1 | 4 | 56 | 7 | 10 |
   | 2 | 3 | 53 | 8 | 11 |
   | 3 | 7 | 58 | 6 | 9  |
   | 4 | 9 | 55 | 7 | 12 |

2. a) How does Rule Based Classifier work? Explain with suitable example. **[7]**

   b) When do we use classifier? You have the following information about the flower. Your job is to classify the given flower with SepalLength = 7, SepalWidth = 3.2, PetalLength = 4.7, and PetalWidth = 1.4. Use KNN algorithm for K = 3 with Euclidean distance matrix. **[3+6]**

   | Id | Sepal_Lenth | Spal_Width | Petal_Lenth | Petal_Width | Labal |
   |----|-------------|------------|-------------|-------------|-------|
   | 1 | 5.1 | 3.5 | 1.4 | 0.2 | setosa |
   | 2 | 4.9 | 3   | 1.4 | 0.2 | setosa |
   | 3 | 4.7 | 3.2 | 1.3 | 0.2 | setosa |
   | 4 | 6   | 2.2 | 4   | 1   | versicolor |
   | 5 | 6.1 | 2.9 | 4.7 | 1.4 | versicolor |
   | 6 | 5.6 | 2.9 | 3.6 | 1.3 | versicolor |
   | 7 | 6.7 | 3.1 | 4.4 | 1.4 | versicolor |

3. a) What is FP-Growth Algorithm? Explain FP-Growth Algorithm with example. **[2+5]**

   b) What is Association Analysis? Explain with different use cases? Use the Apriori algorithm to find the frequent itemsets. Assume minimum support count is 4 and confidence is 80%. **[2+7]**

   | TID | Items |
   |-----|-------|
   | T100 | F, A, C, D, G, I, M, P, N |
   | T101 | A, B, C, D, F, L, M, O, P |
   | T102 | B, F, H, V, J, O, P |
   | T103 | B, C, K, S, A, V |
   | T104 | L, A, F, C, E, P, M, N, V |
   | T105 | I, B, A, P, S, M |
   | T106 | F, A, C, I, B, A, P |

4. a) When do we use clustering? How do you evaluate the cluster generated? **[3+4]**

   b) What is hierarchical clustering? Use this clustering approach to draw dendrogram for given data points. **[2+7]**

   |    | p1 | p2 | p3 | p4 | p5 | p6 |
   |----|----|----|----|----|----|----|
   | p1 | 0.00 | 0.24 | 0.22 | 0.37 | 0.34 | 0.23 |
   | p2 | 0.24 | 0.00 | 0.15 | 0.20 | 0.14 | 0.25 |
   | p3 | 0.22 | 0.15 | 0.00 | 0.15 | 0.28 | 0.11 |
   | p4 | 0.37 | 0.20 | 0.15 | 0.00 | 0.29 | 0.22 |
   | p5 | 0.34 | 0.14 | 0.28 | 0.29 | 0.00 | 0.39 |
   | p6 | 0.23 | 0.25 | 0.11 | 0.22 | 0.39 | 0.00 |

5. a) What is Web Mining? Briefly explain structure of Web Mining. **[3+5]**

   b) Explain different types of outlier with suitable examples. How density based outlier detection works? **[5+3]**

---

## p3 — 2081 Baishakh, Back, BEX/BCT, CT72502 (Elective I)

1. a) What is Data mining? Explain the steps of KDD process briefly. **[2+5]**

   b) What is Data Pre-Processing? Briefly explain the major tasks performed in data pre-processing. **[2+7]**

2. a) How does Neural Net work classified work? Explain with suitable example. **[8]**

   b) What is limitation of Naive Bayes and how Bayesian Belief Networks overcomes it? If a person does exercise, eats an unhealthy diet and has blood pressure but no chest pain, will that person has a heart disease? **[3+5]**

   *(FIGURE — Bayesian belief network, cropped to `images/dm_81ba_bbn.png`.
   Nodes: Exercise, Diet → Heart Disease → Chest Pain, Blood Pressure.
   Priors: Exercise=Yes 0.7 / Exercise=No 0.3; Diet=Healthy 0.25 / Diet=Unhealthy 0.75.
   HD CPT over (D=Healthy,E=Yes)(D=Healthy,E=No)(D=Unhealthy,E=Yes)(D=Unhealthy,E=No):
   HD=Yes → 0.25, 0.45, 0.55, 0.75; HD=No → 0.75, 0.55, 0.45, 0.25.
   CP CPT: CP=Yes → 0.8 (HD=Yes), 0.01 (HD=No); CP=No → 0.2, 0.99.
   BP CPT: BP=High → 0.85 (HD=Yes), 0.2 (HD=No); BP=Low → 0.15, 0.8.)*

3. a) When do we use Association analysis? Explain FP-Tree with an example. **[2+5]**

   b) What is limitation of Apriori algorithm compared to FP-growth? A database has 5 transactions, given in table below. Let min support = 60% and min confidence = 80%. **[2+7]**

   | TID | Item_bought |
   |-----|-------------|
   | T100 | {M, O, N, K, E, Y} |
   | T200 | {D, O, N, K, E, Y} |
   | T300 | {M, A, K, E} |
   | T400 | {M, U, C, K, Y} |
   | T500 | {C, O, O, K, I, E} |

   i) Find all frequent itemsets using FP-growth.
   ii) List all of the strong association rules (with support and confidence).

4. a) What is Cluster Analysis? What are its applications? Explain different types of clusters. **[8]**

   b) Use K-means clustering to cluster the following given data for K = 2 with Euclidean distance matrix. List down the demerits of this algorithm. **[5+3]**

   *(NOTE: no data table is printed on the paper for 4 b — the question jumps
   straight to Q5. Transcribed as printed.)*

5. a) Explain briefly the key steps in text mining. How do you find page rank? Explain. **[4+4]**

   b) What is Anomaly Detection? Why is Anomaly Detection important? Briefly explain different types of anomaly detection schemes. **[2+2+4]**

---

## p4 — BLANK

---

## p5–p6 — 2080 Baishakh, Back, BCT/BEX, CT72502 (Elective-I)

1. What is data warehousing? Explain with example where data warehouses are used. **[2+4]**

2. a) List down the different types of similarity measures by highlighting their application areas. **[3]**

   b) Consider the following table: **[2+2+2+1]**

   | Name | Gender | Eyecolor | Haircolor | Test-1 | Test-2 | Fever | Cough |
   |------|--------|----------|-----------|--------|--------|-------|-------|
   | Ram   | M | Black | Gray  | P | N | P | N |
   | Laxmi | F | Blue  | Black | P | P | N | N |
   | Shyam | M | Blue  | Gray  | N | P | N | P |

   i) Calculated Jaccard Coefficient of Sim<sub>jacard</sub> (Ram, Laxmi) for asymmetric binary attributes.
   ii) Dissimilarity of symmetric binary attributes d (Laxmi, Shayam).
   iii) Find the Simple matching coefficients of SMC (Ram, Shyam).
   iv) Find the Cosine similarity between documents d1 = (4, 1, 2, 0, 2, 0, 0) and d2 = (2, 1, 3, 0, 1, 1, 1)

3. In what cases you cannot use Accuracy for performance measure, give some examples. Assume that you have the following confusion matrix. Calculate the Classification error, Sensitivity, False alarm rate Specificity. **[3+5]**

   |                  |       | Actual Values — True | Actual Values — False |
   |------------------|-------|------|------|
   | Predicated Values | True  | 1050 | 250  |
   | Predicated Values | False | 150  | 950  |

4. What is Nearest Neighbor Classifier? What are the main issues with this classifier? Propose another classifier that solves the issues. **[1+3+4]**

5. Generally, we will be more interested in associated rules with high confidence. However, often we will not be interested in association rules that have a confidence of 100%. Why? Then specifically explain why association rules with 99% confidence may be interesting (i.e., what might they indicate)? Identify the candidate and large item sets of the following transaction table using Apriori algorithm with minimum support 2. **[4+5]**

   | TID | Items |
   |-----|-------|
   | 10 | A, C, D |
   | 20 | B, C, E |
   | 30 | A, B, C, E |
   | 40 | B, E |

6. Where is association analysis applicable and beneficial for us? Elaborate FP Growth Method Algorithm with examples. **[2+6]**

7. Cluster the following samples based on complete-linkage algorithm and draw the dendrogram. Using Euclidean distance. **[8]**

   | Point | x Coordinate | y Coordinate |
   |-------|--------------|--------------|
   | p1 | 0.40 | 0.53 |
   | p2 | 0.22 | 0.38 |
   | p3 | 0.35 | 0.32 |
   | p4 | 0.26 | 0.19 |
   | p5 | 0.08 | 0.41 |
   | p6 | 0.45 | 0.30 |

8. Describe K-means algorithm for clustering and discuss strategy in determining the optimal value of K. **[4+4]**

9. What is anomaly detection? Explain distance based method for anomaly detection. **[2+3]**

10. Write short notes on the following: **[2×5]**

    a) Neural Network Classifier
    b) Time Series Data Mining

---

## p7–p8 — 2079 Bhadra, Regular, BEX/BCT, CT72502 (Elective I)

1. What is Data Mining? What are the steps involved in knowledge discovery process? **[1+5]**

2. Explain typical OLAP operations over a multidimensional data warehouse? Differentiate between OLAP and OLTP tools. **[6+4]**

3. Draw decision tree for the given data using ID3 algorithm. **[10]**

   | Age | Income | Student | Credit_Rating | Buy's_Computer |
   |-----|--------|---------|---------------|----------------|
   | Youth | High | No | Fair | No |
   | Youth | High | No | Excellent | No |
   | Middle_Aged | High | No | Fair | Yes |
   | Senior | Medium | No | Fair | Yes |
   | Senior | Low | Yes | Fair | Yes |
   | Senior | Low | Yes | Excellent | No |
   | Middle_Aged | Low | Yes | Excellent | Yes |
   | Youth | Medium | No | Fair | No |
   | Youth | Low | Yes | Fair | Yes |
   | Senior | Medium | Yes | Fair | Yes |
   | Youth | Medium | Yes | Excellent | Yes |
   | Middle_Aged | Medium | No | Excellent | Yes |
   | Middle_Aged | High | Yes | Fair | Yes |
   | Senior | Medium | No | Excellent | No |

4. Suppose you have a test record "X = (Home Owner = No, Material Status = Married, Income = $120K)". Your job is to classify this record using Naive Bayesian Classification. Use the following table for your calculations. **[6]**

   | Tid | Home Owner | Marital Status | Annual Income | Defaulted Borrower |
   |-----|------------|----------------|---------------|--------------------|
   | 1  | Yes | Single   | 125K | No  |
   | 2  | No  | Married  | 100K | No  |
   | 3  | No  | Single   | 70K  | No  |
   | 4  | Yes | Married  | 120K | No  |
   | 5  | No  | Divorced | 95K  | Yes |
   | 6  | No  | Married  | 60K  | No  |
   | 7  | Yes | Divorced | 220K | No  |
   | 8  | No  | Single   | 85K  | Yes |
   | 9  | No  | Married  | 75K  | No  |
   | 10 | No  | Single   | 90K  | Yes |

5. Derive association rule for the following market basket transactions. **[8]**
   Minimum support = 50%
   Minimum confidence = 80%

   | Transaction ID | Item Set |
   |----------------|----------|
   | 1 | A,B |
   | 2 | A,D |
   | 3 | A,C |
   | 4 | B,E |
   | 5 | B,D,E |
   | 6 | A,E,C |

6. a) How do you handle the categorical attributes in data mining process? Explain with example. Generate the at least four subsequences from the given sequence: < {2,3,5}, {6,7,8}, {9,1}, {7,4} >. **[3+3]**

   b) What are subgraph pattern? **[2]**

7. What are core, border and noise points? Write the algorithm of DBSCAN clustering and explain how it is useful in handling the noisy data. **[3+5]**

8. An internet marketer is interesting in segmenting internet based the input attributes – top ten search key words used, top 10 URLs, recent 10 online purchases (vendor, product, qty, amt), Internet usage level, heaviest access hour, and heaviest access day of a week. Which clustering algorithm do you think can be used for segmentation? How do you validate the cluster which has been created? **[2+6]**

9. What do you mean by anomaly detection? Why is it important and where is it applicable? **[3+3]**

10. Write short notes on: **[2×5]**

    a) Page Rank algorithm
    b) FP-Tree

---

## p9–p10 — 2078 Bhadra, Regular, BEX/BCT, CT 72502 (Elective I)

1. Explain how data mining system can be integrated with database/data warehouse system. Explain Data mining process with diagram. **[4+2]**

2. Suppose that a data warehouse consists of the four dimensions data, spectator, location, and game, and the two measures count and charge, where charge is the fare that a spectator pays when watching a game on a given date. Spectators may be students, adults or seniors, with each category having its own charge rate. **[3+3]**

   a) Draw a star schema diagram for the data warehouse.
   b) Starting with the base cuboid [data, spectator, location, game], what specific OLAP operations should you perform in order to list the total charge paid by student spectators at Dashrath Stadium in 2021?

3. Use the following methods to normalize the data: 200, 300, 400, 600 and 1000. **[2+2+2]**

   a) Min-max normalization by setting min=0 and max=1
   b) Z-score normalization
   c) Normalization by decimal scaling

4. Construct a decision tree for the following data set using information gain. **[8]**

   Predict the class label for a data point with values<Female, 2, standard, high>

   | Gender | Car ownership | Travel cost | Income level | Transport mode |
   |--------|---------------|-------------|--------------|----------------|
   | Male   | 0 | Cheap     | Low    | Bus   |
   | Male   | 1 | Cheap     | Medium | Bus   |
   | Female | 0 | Cheap     | Low    | Bus   |
   | Male   | 1 | Cheap     | Medium | Bus   |
   | Female | 1 | Expensive | High   | Car   |
   | Male   | 2 | Expensive | Medium | Car   |
   | Female | 2 | Expensive | High   | Car   |
   | Female | 1 | Cheap     | Medium | Train |
   | Male   | 0 | Standard  | Medium | Train |
   | Female | 1 | Standard  | Medium | Train |

5. Consider the given transactional database from a grocery store. Use a support threshold of 33.34% and confidence threshold of 60% to compute the following: **[4+4]**

   a) Build a frequent pattern tree (FP-Tree). Show for each transaction how the tree evolves.
   b) Use FP-Growth algorithm to discover the frequent itemsets from this FP-tree.

   | Transcation ID | Items |
   |----------------|-------|
   | T1 | HotDogs, Buns, Ketchup |
   | T2 | HotDogs, Buns |
   | T3 | HotDogs, Coke, Chips |
   | T4 | Chips, Coke |
   | T5 | Chips, Ketchup |
   | T6 | HotDogs, Coke, Chips |

6. Calculate: Accuracy, TPR, FPR and Precision for the given confusion matrix for a classifier. **[4]**

   |                 |         | Actual Class — Class 1 | Actual Class — Class 2 |
   |-----------------|---------|------|-----|
   | Predicted Class | Class 1 | 142  | 40  |
   | Predicted Class | Class 2 | 98   | 720 |

7. Explain Naive Baiyesian classification algorithm with suitable example. **[6]**

8. Write K-means clustering algorithm. Generate two clusters from following dataset using K-means clustering. **[2+6]**

   | Instance | A | B |
   |----------|---|---|
   | 1 | 1   | 2   |
   | 2 | 2.5 | 1   |
   | 3 | 3.5 | 1.5 |
   | 4 | 4   | 1   |
   | 5 | 3.5 | 2.5 |
   | 6 | 5   | 3   |

9. Provide answers to the following with regard to the DBSCAN clustering approach: **[2+2+2]**

   a) How does the DBSCAN quantify the neighborhood of an object? How is a large dense region assembled from small dense regions centered by core objects?
   b) How does DBSCAN find clusters? How are the neighborhood threshold (Epsilion) and minimum number of points (MinPts) determined empirically in DBSCAN?
   c) Prove that in DBSCAN, for a fixed minimum number of points (MinPts) value and two neighborhood thresholds, Epsilion1 < Epsilion2, a cluster (C) with respect to Epsilion1 and MinPts must be a subset of a subset of a cluster (K) with respect to Epsilion2 and MinPts.

10. Compare and contrast among three difference methods of anomaly detection. **[6]**

11. Write short notes on: **[4×4]**

    a) Minkowski Distance
    b) Laplacian Correction in Classification method
    c) Page rank algorithm in Web mining
    d) Overfitting problem in classification

---

## p11–p14 — 2076 Chaitra, Regular, BEX/BCT, CT72502 (Elective I)

1. Find the principal components and the proportion of the total variance explained by each when the covariance matrix of the three random variables X₁, X₂, and X₃ is: **[4]**

   Σ = [ 1 −2 0 ; −2 5 0 ; 0 0 2 ]

2. (a) Given the following points compute the distance matrix using the Manhattan and the Supremum distance. **[2+1+2]**

   | Points | X | Y |
   |--------|---|---|
   | P1 | 6 | 3 |
   | P2 | 2 | 2 |
   | P3 | 3 | 4 |

   (b) Given the following two vectors compute the Cosine similarity between them.
   D1 = [4 0 2 0 1]
   D2 = [2 0 0 2 2]

   (c) Given the following two binary vectors compute the Jaccard similarity and Simple Matching Coefficient.
   P = [0 0 1 1 0 1]
   Q = [1 1 1 1 0 1]

3. Suppose that a data warehouse for a sales company consists of five dimensions: *time, location, supplier, brand,* and *product*, and two measures: *count* and *price*. **[3+3]**

   (a) Draw a *snowflake schema* diagram for the data warehouse.
   (b) Starting with the base cuboid [*time, location, supplier, brand, product*], what specific OLAP operations should one perform in order to list the total *count* for a certain *brand* for each *state* per *year* (assume *location* has three levels: *country, state, city*; and assume *time* has three levels: *year, month, day*)?

4. Why is a conflict resolution strategy often necessary for rule-based classifiers? Describe the common conflict resolution strategies for rule-based classifiers. **[2+4]**

5. The following dataset will be used to train a decision tree for predicting whether a mushroom is edible or not based on its shape, color and odor. **[2+5]**

   | Shape | Color | Odor | Edible |
   |-------|-------|------|--------|
   | C | B | 1 | Yes |
   | D | B | 1 | Yes |
   | D | W | 1 | Yes |
   | D | W | 2 | Yes |
   | C | B | 2 | Yes |
   | D | B | 2 | No |
   | D | G | 2 | No |
   | C | U | 2 | No |
   | C | B | 3 | No |
   | D | W | 3 | No |

   (a) Which attribute would the ID-3 algorithm choose to use for the root of the decision tree?
   (b) Draw the full decision tree that would be learned for the given data.

6. Consider the multi-layer feed-forward neural network shown in the following figure. This neural network has three inputs (x₁), (x₂) and (x₃) connected to a hidden layer consisting of two nodes (h₁) and (h₂). The weight of the edge connecting (xᵢ) to (hⱼ) is (w<sub>ji</sub>). The two hidden nodes are connected to the output node (o). The weight of the edge connecting the hidden node (hᵢ) to the output node (o) is (uᵢ). The activation functions at hidden and output layers is set to sigmoid function defined as follows: **[2+3+4]**

   σ(θ) = 1 / (1 + exp(−θ))

   Using the target output (t), the squared error is used as the loss function at the output node, and is defined as:

   E(o, t) = ½ (o − t)²

   *(FIGURE — 3-input / 2-hidden-node / 1-output network, cropped to `images/dm_76ch_ann.png`.)*

   (a) Using the symbols given above, compute the activation at (h₁).
   (b) Compute the gradient of the loss with respect to the output (o).
   (c) Compute the gradient of the loss with respect to the weight (w₁₂).

7. Consider the transaction data shown in the following table from a fast food restaurant. **[5+3]**

   | Meal Item | List of Item IDs |
   |-----------|------------------|
   | Order:1 | M1, M2, M5 |
   | Order:2 | M2, M4 |
   | Order:3 | M2, M3 |
   | Order:4 | M1, M2, M4 |
   | Order:5 | M1, M3 |
   | Order:6 | M2, M3 |
   | Order:7 | M1, M3 |
   | Order:8 | M1, M2, M3, M5 |
   | Order:9 | M1, M2, M3 |

   There are 9 distinct transactions (Order: 1 – Order: 9) and each transaction involves between 2 and 4 meal items. There are a total of 5 meal items that are involved in the transactions. For simplicity, the meal items have been assigned short names (M1-M5). Assume that the minimum support is 2/9 and the minimum confidence is 7/9.

   (a) Apply the Apriori algorithm to the dataset of transactions and identify all frequent k-itemsets.
   (b) Find all strong association rules of the form: X ∧ Y → Z and note their confidence values.

8. (a) List all the 4-subsequences contained in the data sequence: < {1,3} {2} {2,3} {4} > **[3+3]**

   (b) Draw all candidate sub-graphs obtained from joining the pair of graphs shown below using edge-growing method to expand the sub-graphs.

   *(FIGURE — pair of labelled graphs joined by "+", cropped to `images/dm_76ch_subgraph.png`.)*

9. Given the matrix (X) whose rows represent different data points, perform a k-means clustering on this dataset using the Euclidean distance as the distance function. Here (K) is chosen as 3. The center of the 3 clusters are initialized as red (6.2, 3.2), green (6.6, 3.7) and blue (6.5, 3.0). Provide the final cluster centers and comment on the number of iterations required for the clusters to converge. **[8]**

   X = [ 5.9 3.2 ; 4.6 2.9 ; 6.2 2.8 ; 4.7 3.2 ; 5.5 4.2 ; 5.0 3.0 ; 4.9 3.1 ; 6.7 3.1 ; 5.1 3.8 ; 6.0 3.0 ]

10. The table below is a distance matrix for six objects: **[4+4]**

    |   | A | B | C | D | E | F |
    |---|---|---|---|---|---|---|
    | A | 0 |   |   |   |   |   |
    | B | 0.12 | 0 |   |   |   |   |
    | C | 0.51 | 0.25 | 0 |   |   |   |
    | D | 0.84 | 0.16 | 0.14 | 0 |   |   |
    | E | 0.28 | 0.77 | 0.70 | 0.45 | 0 |   |
    | F | 0.34 | 0.61 | 0.93 | 0.20 | 0.67 | 0 |

    (a) Show the final result of hierarchical clustering with single-link by drawing a dendrogram.
    (b) Show the final result of hierarchical clustering with complete-link by drawing a dendrogram.

11. (a) Discuss the issues related to anomaly detection. **[2]**

    (b) If the probability that a normal object is classified as an anomaly is 0.01 and the probability that an anomalous object is classified as anomalous is 0.99, then what is the false alarm rate and detection rate if 99% of the objects are normal? **[3]**

12. Consider the following subset of pages and their links. Apply the PageRank algorithm using a damping factor of 0.85. A minimum of five iterations are required. Assume initial page rank of all pages is 0.25. **[8]**

    *(FIGURE — four pages A/B/C/D with links, cropped to `images/dm_76ch_pagerank.png`.)*

---

## p15 — 2076 Ashwin, Back, BEX/BCT, CT72502 (Elective I)

1. What are the fundamental differences between Data Mining and Data Warehousing? Describe the steps of KDD for data mining. **[3+7]**

2. What do you mean by dimensional data? What are base & apex cuboid? Slicing & Dicing? Roll Down and Roll UP operations? Give example. **[2+3+3+3]**

3. How do you measure the accuracy of classifiers? How do you select best root attribute in decision tree? Explain. **[4+6]**

4. What are prior and posterior probabilities? Explain the algorithmic steps of Bayesian classifier and write its strengths. **[3+7]**

5. For the transactions given below, consider confidence=60% and minimum support=30%. Identify large itemsets (L-Itemset) at L=3 with possible associations using A-priori algorithm and generate F-List using FP-Growth algorithm. **[12]**

   | Transactions | Items description |
   |--------------|-------------------|
   | T1 | A, B, C, T, M, P, D, K |
   | T2 | A, B, T, P, D, K |
   | T3 | B, C, T, D, M, A, P |
   | T4 | A, C, T, M, D, |
   | T5 | A,C, D, K, M |
   | T6 | B, C, T |

6. How DBSCAN algorithm works? How do we avoid the issues of DBSCAN? **[8+2]**

7. Explain web mining taxonomy. **[8]**

8. Write short notes on (**Any Three**) **[3+3+3]**

   a. Data smoothing techniques
   b. Clustering and its application in anomaly detection
   c. AprioriALL: Sequential pattern mining algorithm
   d. Various similarity measures between data tuples.

---

## p16 — 2075 Chaitra, Regular / Back, BEX/BCT, CT72502 (Elective I)

1. Explain Data Warehouse architecture with its analytical processing. **[8]**

2. Why data preprocessing is necessary? Explain the methods for data preprocessing to maintain data quality. **[4+4]**

3. Define Decision Tree Classifier with Gini-Index with suitable example. How can you handle overfitting in Decision Tree? **[6+4]**

4. What do you mean by frequent Pattern growth, draw FP-tree with given tabular data. **[4+4]**

   | TID | Items |
   |-----|-------|
   | 01 | f, a, c, d, g, i, m, p |
   | 02 | a, b, c, f, l, m, o |
   | 03 | b, f, h, j, o, w |
   | 04 | b, c, k, s, p |
   | 05 | A, f, c, e, l, p, m, n |

5. How ANN works? Explain with Algorithm. **[8]**

6. What is the application of clustering in data mining? Explain K-means clustering with example. **[2+6]**

7. How DBSCAN clustering is used for handling noise in data? **[8]**

8. What is outlier? Explain the distance base approaches for the anomaly detection. **[5]**

9. What are the challenges of web mining? Explain about time series data mining with an example. **[5]**

10. Write short notes on: (Any three) **[4+4+4]**

    a) Market Basket Analysis
    b) Visual Data Mining
    c) OLAP and OLTP
    d) Data Normalization

---

## p17 — 2075 Ashwin, Back, BCT/BEX, CT72502 (Elective I)

1. How is data warehouse different from a database? How are they similar? **[2+2]**

2. Discuss issues to consider during Data Integration. Describe OLAP and operations on OLAP with suitable example. **[5+5]**

3. Explain Naïve Bayesian classification with suitable example. **[8]**

4. The confusion matrix for a classifier is given as follows: **[10]**

   |              |         | Predicted Class — Class 1 | Predicted Class — Class 2 |
   |--------------|---------|----|----|
   | Actual Class | Class 1 | 21 | 6  |
   | Actual Class | Class 2 | 7  | 41 |

   Calculate: Accuracy, Sensitivity, Specificity and Precision.

5. Why association analysis is required in data mining? Explain Apriori principle with example. **[2+6]**

6. What are the advantages of FP growth method? Explain FP growth algorithm. **[2+6]**

7. Explain K-means clustering with limitation. Generate two clusters from following dataset using K-means clustering. **[4+6]**

   | A | B |
   |---|---|
   | 1   | 2   |
   | 2.5 | 4.5 |
   | 4   | 6   |
   | 3.5 | 4   |
   | 4   | 5.5 |
   | 3   | 6   |

8. What are outliers? Explain an algorithm that can be used to generate density based clusters. **[8]**

9. Why anamoly detection is important? Explain distance based method for anamoly detection. **[2+6]**

10. Explain Web mining and Multimedia mining. **[6]**

---

## p18 — 2074 Chaitra, Regular, BEX/BCT, CT72502 (Elective I)

1. What is data warehouse and data mart? Describe Snowflake scheme with example. **[2+4]**

2. What are the approaches to handle missing data? Describe OLAP and operations on OLAP with suitable example. Differentiate between OLAP and OLTP. **[2+5+3]**

3. Draw clear block diagram depicting different stages in classification. Explain the inverse relation between precision and recall. Given the confusion matrix, determine accuracy, sensitivity and precision of the classifier model. **[2+3+5]**

   | Actual \ Predicted | Positive | Negative |
   |--------------------|----------|----------|
   | Positve  | 142 | 40  |
   | Negative | 98  | 720 |

4. Explain decision tree with the concept of Naive base classification with appropriate example. **[10]**

5. Why association analysis is required in data mining? Explain apriori principle with example. **[2+6]**

6. How does FP growth approach overcomes the disadvantages of Apriori algorithm. For the transaction data given in table generate FP-Tree. **[2+8]**

   | Transaction ID | Item set |
   |----------------|----------|
   | T1 | Camera, Laptop, Pen drive |
   | T2 | Laptop, Pen drive |
   | T3 | Laptop, Mobile, Earphone |
   | T4 | Earphone, Mobile |
   | T5 | Camera, Earphone |
   | T6 | Laptop, Mobile, Earphone |

7. Describe the difference between Hierarchical and partitioning clustering. How K-means clustering is applied? Verify using example. **[2+8]**

8. What do you mean by anomaly detection and why is it important? Describe distance based approaches for anomaly detection. **[4+3]**

9. Write short notes on: (any three) **[3×3]**

   i) Issues in clustering
   ii) Multimedia mining
   iii) Time series data mining
   iv) Web mining

---

## p19–p20 — 2074 Ashwin, Back, BEX/BCT, CT72502 (Elective I)

1. What is data mining? Explain the process of data mining. **[2+3]**

2. In real-world data, tuples with missing values for same attributes are a common occurrence. Describe various methods for handling this problem. **[5]**

3. What is classification? Explain Rule-Based classification with its classification principles with suitable example. **[2+8]**

4. The confusion matrix for a classifier is given as follows: **[10]**

   |              |         | Predicted Class — Class 1 | Predicted Class — Class 2 |
   |--------------|---------|----|----|
   | Actual Class | Class 1 | 25 | 9  |
   | Actual Class | Class 2 | 4  | 31 |

   Calculate:
   a) Accuracy   b) Sensitivity
   c) Specificity   d) Precision

5. Identify the candidate, frequent item sets and association rules for the following transaction data using Apriori algorithm. **[8]**

   | TID | ITEMS |
   |-----|-------|
   | 1 | M1, M2, M5 |
   | 2 | M2, M4 |
   | 3 | M2, M3 |
   | 4 | M1, M2, M4 |
   | 5 | M1, M3 |
   | 6 | M2, M3 |
   | 7 | M1, M3 |
   | 8 | M1, M2, M3, M5 |
   | 9 | M1, M2, M3 |

   Take minimum support = 20%, minimum confidence 80%

6. Explain FP-Growth algorithm with example. **[8]**

7. Write K-means algorithm and find clusters for following data set. **[2+8]**

   | Instance | X | Y |
   |----------|---|---|
   | 1 | 1.0 | 2.0 |
   | 2 | 2.5 | 1.0 |
   | 3 | 3.5 | 1.5 |
   | 4 | 4.0 | 1.0 |
   | 5 | 3.5 | 2.5 |
   | 6 | 5.0 | 3.0 |

   (Take K = 2)

8. What is web mining? Explain different categories of web mining. **[6]**

9. List the various types of partition based clustering methods. Explain Hierarchical clustering method with an example. **[10]**

10. Write short notes on: (Any two) **[2×4]**

    a) OLAP Operations
    b) Density reachable and Density Connected
    c) Data Mining for Anomy Detection

---

## p21 — 2073 Shrawan, New Back (2066 & Later Batch), BE/BCT, CT72502 (Elective II)

1. "The world is data rich but information is poor". Justify with your own words. **[8]**

2. What are the measuring elements of data Quality? Explain different data transformation by normalization methods with an example. **[2+6]**

3. What is a decision tree and how information gain is used for attribute selection? Explain with example. **[8]**

4. Explain ROC. Using the following data, calculate TPR, FPR, precision for given confusion matrix. **[1+3+6]**

   |   | A | B |
   |---|---|---|
   | A | 20 | 5 |
   | B | 10 | 40 |

   Classify, A = Yes, B = No

5. What is FP Tree? How FP-growth algorithm eliminate the problem of Apriori algorithm? Construct the FP tree and find association rules for the following transaction database using FG- Growth algorithm. Support = 30% and confidence = 75%. **[10]**

   | Transaction ID | Items |
   |----------------|-------|
   | 1 | P,R,S |
   | 2 | R,S,T |
   | 3 | P,Q,R |
   | 4 | P,R,S,T |
   | 5 | P,S,T |
   | 6 | P,Q,T |
   | 7 | Q,S,T |
   | 8 | Q,R,T |

6. What are Categorical data? What are the possible issues arrives when using Categorical data? How can you handle such issues? **[2+3+3]**

7. What is the application of clustering in data mining? Explain the k-means algorithm with example. **[8]**

8. What is anamoly detection? Explain distance based method for anamoly detection. **[8]**

9. Write short notes on: **[4×3]**

   i) Data transformation
   ii) Web mining
   iii) OLAP

---

## p22 — 2072 Chaitra, Regular, BEX/BCT, CT72502 (Elective II)

1. What is data mining? Explain all the steps of knowledge discovery. **[2+6]**

2. How do you perform analysis of multidimensional data? Explain with the concept of OLAP. **[10]**

3. Predict Class label using naive Bayesian classifier for X = (age = youth, income = medium, student = yes, credit-rating = fair) using the following data set. **[10]**

   | RID | Age | Income | Student | Credit-rating | Class Buy computer |
   |-----|-----|--------|---------|---------------|--------------------|
   | 1  | Youth | High | No | Fair | No |
   | 2  | Youth | High | No | Excellent | No |
   | 3  | Middle-age | High | No | Fair | Yes |
   | 4  | Senior | Medium | No | Fair | Yes |
   | 5  | Senior | Low | Yes | Fair | Yes |
   | 6  | Senior | Low | Yes | Excellent | No |
   | 7  | Middle-age | Low | Yes | Excellent | Yes |
   | 8  | Youth | Medium | No | Fair | No |
   | 9  | Youth | Low | Yes | Fair | Yes |
   | 10 | Senior | Medium | Yes | Fair | Yes |
   | 11 | Youth | Medium | Yes | Excellent | Yes |
   | 12 | Middle-age | Medium | No | Excellent | Yes |
   | 13 | Middle-age | High | Yes | Fair | Yes |
   | 14 | Senior | Medium | No | Excellent | No |

4. The confusion matrix for a classifier is given as follows: **[10]**

   |                 |        | actual class — class1 | actual class — class2 |
   |-----------------|--------|----|----|
   | predicted class | class1 | 21 | 6  |
   | predicted class | class2 | 7  | 41 |

   calculate a. accuracy  b. sensitivity  c. specificity  d. precision  e. recall

5. What is the importance of SUPPORT and COFIDENCE during association analysis? Explain FP-Growth method with example. **[10]**

6. What are the types of clustering methods? Explain DBSCAN method of clustering with an example. **[10]**

7. What is the use of Apriori Algorithm in market basket analysis? Explain with suitable example. **[10]**

8. Write short notes on: **[4×3]**

   i) Time series Data mining
   ii) Issues in anomaly/Fraud detection
   iii) Categorical data and related issues

---

## p23 — 2071 Chaitra, Regular, BEX/BCT, CT72502 (Elective I)

*(Rubric line 3 on this paper reads "All questions carry equal marks." — no per-question
marks are printed. Full Marks 80 over 8 questions = 10 each.)*

1. What is a Data Mining? Explain its application.

2. Explain the properties that a Distance Metric needs to support with respect to Minkowski's distance.

3. What is a decision tree? Explain Gini Index with suitable example.

4. Explain a Bayes classifier. In what cases can Naive Bayes and Bayesian Belief Network be used?

5. Why is a clustering an unsupervised learning? How can hierarchical clusters be generated using Bisecting K-means algorithm?

6. Explain the different measures of cluster validity.

7. How does Apriori Algorithm optimize the brute force approach for frequent item set generation?

8. What is an Anomaly Detection? Explain few distance based approaches that can be used for Anomaly Detection.

---

## p24 — 2072 Kartik, New Back (2066 & Later Batch), BEX/BCT, CT72502 (Elective I)

1. What is a data mining? Explain general steps in brief. **[4]**

2. Why data preprocessing is required in the data mining? Explain some of approaches of data clearing. **[5+5]**

3. Write about Hunt's Algorithm for Decision Tree induction. Explain the test conditions that can be used for different attribute types. **[10]**

4. What is an ANN classifier? Explain its general consideration that required for the classifier. **[2+6]**

5. What is an association analysis? Explain its importance in market-basket analysis. **[2+5]**

6. What is a Frequent item set? Explain FP growth method with example. **[1+8]**

7. What is a cluster analysis? How it is different from classification? **[5]**

8. Explain a DBSCAN algorithm with example. **[7]**

9. What is an Anomaly detection? Discuss its importance in security. **[5]**

10. Explain Time series data mining in brief. **[6]**

11. Write short notes on: **[3×3]**

    i) Data transformation
    ii) Sequential pattern
    iii) Cluster evaluation

---

## p25 — 2071 Shawan, New Back (2066 & Later Batch), BEX/BCT, CT72502 (Elective I)

*(Rubric line 3 on this paper reads "All questions carry equal marks." — no per-question
marks are printed.)*

1. What is data mining? Explain different data types of attributes in a dataset.

2. How can principle component analysis be used for dimentionality reduction?

3. Why is classification a super vised learning method? Explain different impurity measures used in decision tree classifier.

4. Explain Naive Bayes classifier. How can over fitting problem be solved in case of classification?

5. Explain FP-growth algorithm in detail.

6. What are association rules? How can spriori algorithm be used to generate association rules.

7. What is contiguous cluster? Explain an algorithm that can be used to generate contiguous clusters.

8. Explain K-means clustering with limitation Use k-means clustering to cluster the following dataset.

   | A | B |
   |---|---|
   | 1.0 | 1.0 |
   | 1.5 | 2.0 |
   | 3.0 | 4.0 |
   | 5.0 | 7.0 |
   | 3.5 | 5.0 |
   | 4.5 | 5.0 |
   | 3.5 | 4.5 |

9. How can Nearest-Neighbor algorithm be used for anomaly defection?

10. Write short notes on:

    a) Time-series data mining
    b) Data warehouse and data mart

---

## p26 — 2070 Chaitra, Regular, BEX/BCT, CT725 (Elective I)

1. a) What is "curve of Dimensionality"? How can it be avoided? **[5]**

   b) Discuss the impact of noisy data in data mining? **[5]**

2. Explain rule based classifier? How can CN2 Algorithm be used for rule based classification? Define "Accuracy" and "Laplace" measures used for rule evaluation. **[9]**

3. An input sequence "A A B B B A A A B B" was used for classification. The Classifier 'X' predicted the sequences as: "A A B B B A A A B B" where as the Classifier 'Y' predicted the sequences as: "A A A A B B A A A B". Develop the corresponding confusion matrix for the classifiers and find their corresponding. **[10]**

   i) Accuracy
   ii) Precision
   iii) True Positive Rate
   iv) False Positive Rate

4. Explain Apriori algorithm. Use Apriori to generate frequent item sets with support of 50% for the following transaction database. **[10]**

   | TID | Items |
   |-----|-------|
   | 1 | ACD |
   | 2 | BD |
   | 3 | ABCE |
   | 4 | BDF |

5. Why is pattern evaluation important in association rule mining? Explain with example the statistical based measures used for measuring interestingness of association rules. **[8]**

6. What is a density based cluster. Explain an algorithm that can be used to generate density based clusters. **[8]**

7. What is Hierarchical Clustering? Differentiate between agglomerative and divisive approach of hierarchical clustering. Augment your answer with appropriate illustrative examples. **[10]**

8. Write short notes on: **[15]**

   i) Data ware house and Data mart
   ii) Base Rate Fallacy
   iii) Web mining
   iv) Anomaly Detection
   v) Convex Hull Method

---

## FIGURES CROPPED FROM THIS SCAN

| File | Source | Content |
|------|--------|---------|
| `images/dm_81ba_bbn.png`       | p3 (2081 Ba) Q2 b  | Bayesian belief network + all CPTs |
| `images/dm_76ch_ann.png`       | p12 (2076 Ch) Q6   | 3-input / 2-hidden / 1-output feed-forward net |
| `images/dm_76ch_subgraph.png`  | p13 (2076 Ch) Q8 b | pair of labelled graphs for edge-growing |
| `images/dm_76ch_pagerank.png`  | p14 (2076 Ch) Q12  | Page A/B/C/D link graph |

Crop method (PyMuPDF, matrix 3.2×, fractional clip rectangle) — see the handoff.

---

## UNCERTAIN / NOTES

* p3 (2081 Baishakh) Q4 b asks to "cluster the following given data" but **no data
  table is printed** on the paper. Transcribed as printed.
* p16 (2075 Chaitra) header cell reads **"Regular / Back"** — it is a combined paper.
  Treated as Regular (bold) in the .tex documents.
* p17 (2075 Ashwin) exam cell is heavily inked over; confirmed **"Back"** by a
  5× zoom crop of the header table.
* p26 (2070 Chaitra) exam cell is faded; reads **"Regular"**. Subject code on this
  paper is **CT725**, not CT72502.
* p1 (2080 Bhadra) Q3 b table row T106 genuinely prints "F, A, C, I, B, A, P"
  (A appears twice); T104 prints "L, A, F, C, E, P, M, N, V".
* p21 (2073 Shrawan) programme cell reads "BE, BCT" (not "BEX, BCT").
