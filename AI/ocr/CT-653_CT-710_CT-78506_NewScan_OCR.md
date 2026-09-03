# AI (CT 653 / CT 710 / CT 78506) — Full OCR of the New PYQ scan

Source file: `New PYQ/AI.pdf` (48 pages, pure image scan — its embedded text layer is
garbage OCR and is useless for anything but a page index).
Transcribed 2026-09-03 with `tools/ocr_page.py` (RapidOCR, CPU), then image-verified
band by band wherever the OCR was unreliable. Verbatim, including the papers' own
typos. Marks are shown as printed, in [square brackets].

**USE THIS FILE INSTEAD OF RE-RENDERING THE PDF.** Only figures still need the PDF;
they were all cropped on 2026-09-03 and are listed under "Figures" below.

This scan holds **THREE course codes**, not two:

| Pages | Code | Subject line | Programme | Year/Part | Papers |
|---|---|---|---|---|---|
| 1-11 | CT 78506 | Artificial Intelligence (Elective III) | BEX (one paper BCT) | IV/II | 8 |
| 12-18 | CT 710 | Artificial Intelligence | BEI | IV/I | 7 |
| 19-48 | CT 653 | Artificial Intelligence | BCT | III/II | 26 |

41 papers in all. Papers 1-2, 3-4, 6-7, 20-21, 23-24, 28-29 and 32-33 each run over
two pages, so **a page is not a paper** — always read the printed header.

All papers: BE, Full Marks 80, Pass Marks 32, Time 3 hrs. Rubric on every paper is
"Candidates are required to give their answers in their own words as far as practicable. /
Attempt All questions. / The figures in the margin indicate Full Marks. /
Assume suitable data if necessary."

## Physical page order (verified against each page's own printed header)

| Page | Paper | Exam | Programme / Code | New? |
|------|-------|------|------------------|------|
| 1-2   | 2077 Chaitra  | Regular | BEX / CT 78506 | new |
| 3-4   | 2076 Bhadra   | Regular / Back | BEX / CT 78506 | new |
| 5     | 2074 Magh     | Back | BEX / CT 78506 | new |
| 6-7   | 2074 Bhadra   | Regular | BEX / CT 78506 | new |
| 8     | 2073 Bhadra   | Regular | BEX / CT 78506 | new |
| 9     | 2072 Magh     | New Back (2066 & Later Batch) | **BCT** / CT 78506 | new |
| 10    | 2072 Ashwin   | Regular | BEX / CT 78506 | new |
| 11    | 2071 Bhadra   | Regular / Back | BEX / CT 78506 | new |
| 12    | 2082 Bhadra   | Regular | BEI / CT 710 | new |
| 13    | 2082 Baishakh | Back | BEI / CT 710 | new |
| 14    | 2081 Bhadra   | Regular | BEI / CT 710 | new |
| 15    | 2081 Baishakh | Back | BEI / CT 710 | old p15 |
| 16    | 2080 Bhadra   | Regular | BEI / CT 710 | old p14 |
| 17    | 2080 Baishakh | Back | BEI / CT 710 | old p16 |
| 18    | 2079 Bhadra   | Regular | BEI / CT 710 | old p17 |
| 19    | 2082 Kartik   | Back | BCT / CT 653 | new |
| 20-21 | 2081 Chaitra  | Regular | BCT / CT 653 | new |
| 22    | 2081 Ashwin   | Back | BCT / CT 653 | new |
| 23-24 | 2080 Chaitra  | Regular | BCT / CT 653 | new |
| 25    | 2080 Ashwin   | Back | BCT / CT 653 | new |
| 26    | 2079 Chaitra  | Regular | BCT / CT 653 | old p13 |
| 27    | 2079 Ashwin   | Back | BCT / CT 653 | new |
| 28-29 | 2079 Jestha   | Back | BCT / CT 653 | new |
| 30    | 2078 Chaitra  | Regular | BCT / CT 653 | new |
| 31    | 2078 Poush    | Back | BCT / CT 653 | new |
| 32-33 | 2078 Baishakh | Back | BCT / CT 653 | new |
| 34    | 2077 Chaitra  | Regular | BCT / CT 653 | new |
| 35    | 2076 Baishakh | Back | BCT / CT 653 | new |
| 36    | 2075 Bhadra   | Regular | BCT / CT 653 | new |
| 37    | 2075 Baishakh | Back | BCT / CT 653 | old p12 |
| 38    | 2074 Bhadra   | Regular | BCT / CT 653 | old p11 |
| 39    | 2073 Magh     | New Back | BCT / CT 653 | old p10 |
| 40    | 2073 Bhadra   | Regular | BCT / CT 653 | old p9 |
| 41    | 2072 Magh     | New Back | BCT / CT 653 | old p8 |
| 42    | 2072 Ashwin   | Regular | BCT / CT 653 | old p7 |
| 43    | 2071 Magh     | New Back | BCT / CT 653 | old p6 |
| 44    | 2071 Bhadra   | Regular / Back | BCT / CT 653 | old p5 |
| 45    | 2070 Magh     | New Back | BCT / CT 653 | old p4 |
| 46    | 2070 Bhadra   | Regular | BCT / CT 653 | old p3 |
| 47    | 2069 Poush    | New Back | BCT / CT 653 | old p2 |
| 48    | 2069 Bhadra   | Regular (2066 & Later Batch) | BCT / CT 653 | old p1 |

"old pN" = already transcribed in `CT-653_CT-710_OCR.md` at that page number.
**The new scan is a strict superset of the old one** — unlike DSAP and Wireless,
the old AI scan holds no paper of its own.

## Year codes collide across course codes

The same year code names different papers under different codes. All of these are
real, distinct papers:

| Code | CT 653 | CT 78506 |
|---|---|---|
| 74 Bh | p38 (Regular, BCT) | p6-7 (Regular, BEX) |
| 73 Bh | p40 (Regular, BCT) | p8 (Regular, BEX) |
| 72 Ma | p41 (New Back, BCT) | p9 (New Back, BCT) |
| 72 Ash | p42 (Regular, BCT) | p10 (Regular, BEX) |
| 71 Bh | p44 (Regular / Back, BCT) | p11 (Regular / Back, BEX) |
| 77 Ch | p34 (Regular, BCT) | p1-2 (Regular, BEX) |

**72 Ma collides on programme as well** — both papers print BCT. Only the course
code separates them, so the document's third typographic axis has to key off the
CODE, never the programme.

## Marks checksums

Every paper below carries a marks checksum. All 29 transcribed papers add to
exactly 80, which is what caught three misread marks (p14 Q4, p19 Q6, p5 Q4).
Recompute it before trusting any marks edit.

## Figures (all cropped 2026-09-03)

| Paper | Question | File | What it is |
|---|---|---|---|
| p3-4, 2076 Bh CT 78506 | Q3 | `ai_76bh_bfs.png` | path-finding graph, nodes A-J, for Best First Search |
| p19, 2082 Ka CT 653 | Q7 | `ai_82ka_ann.png` | 2-input feed-forward net, arcs a-f, nodes r1 r2 s1 s2 y |
| p20-21, 2081 Ch CT 653 | Q3 | `ai_81ch_astar.png` | A* cost graph, start S, goal G, heuristics printed on the nodes |
| p20-21, 2081 Ch CT 653 | Q9 | `ai_82ka_ann.png` | same net as p19 Q7, one crop serves both |
| p23-24, 2080 Ch CT 653 | Q3 | `ai_80ch_astar.png` | A* / greedy cost graph, start S, goal G (its heuristic table is typeset in LaTeX, not cropped) |
| p32-33, 2078 Ba CT 653 | Q5 | `ai_78ba_bbn.png` | Cloudy / Sprinkler / Rain / Wet Grass belief net with its CPTs |
| p35, 2076 Ba CT 653 | Q3 | `ai_76ba_minmax.png` | alpha-beta game tree, MAX at top, leaves 3 5 10 / 2 8 19 / 2 7 3 |

`AI/images/ai_79ch_minmax.png` (2079 Chaitra Q3) was already cropped in an
earlier session.

## Defects in the papers themselves

* **p36, 2075 Bhadra Q6** ends "...consist of four individuals with the following
  chromosomes." and then prints **no chromosome list at all**. Confirmed by image
  crop. Same class of defect as Data Mining 2081 Baishakh Q4b.
* **p19, 2082 Kartik Q5** contains a stray "10." inside its sentence list
  ("Fish is an animal 10. Fish lives in water.").
* **p14, 2081 Bhadra Q6** names the dog "Figo" in the first line and "Fido" in
  the next two.

---
## p1-2 — 2077 Chaitra, Regular, BEX, CT 78506 (Elective III), IV/II

1. What is Turing Test and total turing test? Explain PEAS for a self-deriving car. [4+4]
2. Assume you are given two jugs; a 4-gallon one and a 3-gallon one, and a pump which has unlimited water. How can you get exactly 2 gallons of water in the 4-gallon jug? Formalize the problems, write down Production Rules and draw Search Tree for water Jug problem. [2+2+4]
3. Devise an example to show how A* algorithm uses path cost and heuristic cost to generate best solution. [8]
4. Explain forward chaining giving suitable example. [8]
5. If it is sunny and warm day you will enjoy. If it is warm and pleasant day you will do strawberry picking. If it is raining no strawberry picking. If it is raining you will get wet. It is warm day. It is raining. It is sunny. Prove that "You will enjoy" using resolution by refutation. [8]
6. What are Frames and Semantic Net? Convert the given sentences in semantic Net: [2+6]
   - Tweety and Sweety are birds.
   - Tweety has a red beak.
   - Sweety is Tweety's child.
   - A crow is a bird.
   - Birds can fly.
   - Sparrow is a bird.
   - Sparrow has a wing.
7. You are locked on a deserted island. Mushrooms of various types grow widely all over the island but no other food is anywhere to be found. Some of the mushrooms have been determined as poisonous and others as not (Determined by your former companions' trial and error). You are the only on reaming on the island. You have the following data to consider; [8]

   | Example | NotHeavy | Smelly | Spotted | Smooth | Edible |
   |---|---|---|---|---|---|
   | A | 1 | 0 | 0 | 0 | 1 |
   | B | 1 | 0 | 1 | 0 | 1 |
   | C | 0 | 1 | 0 | 1 | 1 |
   | D | 0 | 0 | 0 | 1 | 0 |
   | E | 1 | 1 | 1 | 0 | 0 |
   | F | 1 | 0 | 1 | 1 | 0 |
   | G | 1 | 0 | 0 | 1 | 0 |
   | H | 0 | 1 | 0 | 0 | 0 |
   | U | 0 | 1 | 1 | 1 | ? |
   | V | 1 | 1 | 0 | 1 | ? |
   | W | 1 | 1 | 0 | 0 | ? |

   You know whether or not mushroom A through H are poisonous, but you do not know about U through W. Which attributes should you choose as the root of a decision tree? Give reason.
8. What are the major problems associated with NLP? Explain different steps involved in NLP. [2+6]
9. Why do you need Multilayer Perceptron Neural Networks? Write down the perceptron algorithm and use it to Construct Network which perform like Logical AND Operation and show each calculation performed. [2+6]
10. Write short notes on: [2x4]
    - a) Uninformed search
    - b) Supervised Vs Unsupervised learning

*(Marks checksum 8x10 = 80. rows C, G and U were re-OCR'd at zoom 4.5 on 2026-09-03
and are as printed above.)*

## p3-4 — 2076 Bhadra, Regular / Back, BEX, CT 78506 (Elective III), IV/II

1. Describe Artificial Intelligence and its subfields. What is Total Turing Test? [4+3]
2. How do you define a problem in a state space? In a correctly worked out crypt-arithmetic problem AB + CD = AAA, what could be the possible values of B? Justify your answer. [3+4]
3. Explain how alpha-beta pruning helps us reduce the complexity of adversarial search. Consider a search tree for a path-finding problem as shown. Assuming node A to be the root node and node I to be the goal node, explain how Best First Search reaches the goal by showing changes in the open list, closed list, and path at each step of the search. [4+5]
   *(FIGURE: a labelled path-finding graph, nodes A-I with edge costs. Needs a crop.)*
4. Convert the following into FOL. [2+5]
   - a) Arya hates Joffery and Cersei.
   - b) No Lannister loves Bran.
   - c) Sansa has at least one sister.
   - d) Every Stark hates at least one Lannister.

   What are the steps involved in converting FOL into CNF?
5. Consider the following axioms. [7]
   - All direwolves howl at night.
   - Anyone who has any cat will not have any mice.
   - Lights sleepers do not have anything that howls at night.
   - Jon has either a cat or a direwolf.

   Prove that if Jon is a light sleeper, then Jon does not have any mice using resolution method.
6. What do you understand by structured knowledge representation? Explain semantic nets. [2+5]
7. Differentiate between supervised and unsupervised learning methods. Explain the steps of genetic algorithm with an example. [5+5]
8. Describe Expert System with its architecture. What are its advantages and disadvantages [5+2+2]
9. Explain the steps of Natural Language Processing. Explain syntactic analysis and draw a parse tree for the following sentence. "A girl has a name." [5+4]
10. What are the issues present in knowledge representation in an expert system? A perceptron can learn a linearly separable function when given enough training. Justify with appropriate figures. [2+6]

*(Marks checksum 7+7+9+7+7+7+10+9+9+8 = 80.)*

## p5 — 2074 Magh, Back, BEX, CT 78506 (Elective II as printed), IV/II

1. What is Artificial Intelligence, Knowledge and Learning? "Learning is an essential characteristic for intelligent agents". Comment on this statement. [2+2+2+4]
2. Discuss about Constraints Satisfaction Problem (CSP). Solve the following Crypt-arithmetic problem. [8]

       SEND
     + MORE
     -------
      MONEY

3. Make a detail comparison between Informed and Uniformed search with examples. [8]
4. Why Conjuctive normal form is required? Explain all the steps to convert to CNF. Transform "P->((Q & ~R) > S)" into CNF. [6]
5. Differentiate between Supervised and Unsupervised Learning. Clustering fall under which of the above categories? Justify stating algorithms. [2+4]
6. What are frames and semantic networks? Compare them with suitable examples. [2+5]
7. Differentiate between NLU and NLG. List down the different steps involved in the natural language processing (NLP) with suitable examples. [9]
8. What do you understand by Perceptron? How can we design a neural network that acts as an XOR gate? [10]
9. How best attribute is selected in a decision-tree? Select first best attribute of the decision-tree from given sample data. [8]

   | Outlook | Temperature | Humidity | Windy | Play gold (Target variable) |
   |---|---|---|---|---|
   | Rainy | Hot | High | False | No |
   | Rainy | Hot | High | True | No |
   | Overcast | Hot | High | False | Yes |
   | Sunny | Mild | High | False | Yes |
   | Sunny | Cool | Normal | False | Yes |
   | Sunny | Cool | Normal | True | No |
   | Overcast | Cool | Normal | True | Yes |
   | Rainy | Mild | High | False | No |
   | Rainy | Cool | Normal | False | Yes |
   | Sunny | Mild | Normal | False | Yes |
   | Rainy | Mild | Normal | True | Yes |
   | Overcast | Mild | High | True | Yes |
   | Overcast | Hot | Normal | False | Yes |
   | Sunny | Mild | High | True | No |

10. Write short notes on: [2x4]
    - i) Alpha-beta prunning
    - ii) Self Organizing Map (SOM)

*(Marks checksum 10+8+8+6+6+7+9+10+8+8 = 80. The paper's own typos kept:
"Uniformed", "Conjuctive", "prunning", "Play gold", "Artificial Intelligences".)*
## p6-7 — 2074 Bhadra, Regular, BEX, CT 78506 (Elective III), IV/II

1. What are intelligent agents and how can we design intelligent agent? Explain with examples with relevance to PEAS framework? [4+3]
2. What do understand by Constraint satisfaction problem? Solve the following Crypt-arithmetic problem. [8]

       SEND
     + MORE
     -------
      MONEY

3. Compare breadth first search and depth first search along with examples. [8]
4. State the approach for learning using ID3 and Select the root attribute of the decision-tree from given sample data. [2+7]

   | Outlook | Temperature | Humidity | Windy | Play golf (Target variable) |
   |---|---|---|---|---|
   | Rainy | Hot | High | False | No |
   | Rainy | Hot | High | True | No |
   | Overcast | Hot | High | False | Yes |
   | Sunny | Mild | High | False | Yes |
   | Sunny | Cool | Normal | False | Yes |
   | Sunny | Cool | Normal | True | No |
   | Overcast | Cool | Normal | True | Yes |
   | Rainy | Mild | High | False | No |
   | Rainy | Cool | Normal | False | Yes |
   | Sunny | Mild | Normal | False | Yes |
   | Rainy | Mild | Normal | True | Yes |
   | Overcast | Mild | High | True | Yes |
   | Overcast | Hot | Normal | False | Yes |
   | Sunny | Mild | High | True | No |

5. Assume the following facts: [8]
   - a) Horses, cows, pigs are mammals.
   - b) An offspring of a horse is a horse.
   - c) Bluebeard is a horse.
   - d) Bluebeard is Charlie's parent.
   - e) Offspring and parent are inverse relations.
   - f) Every mammal has a parent.

   Prove Charlie is a horse using resolution refutation
6. "Learning is an essential characteristic for intelligent agents." Comment on this statement. Differentiate between Supervised and Unsupervised Learning. [4+4]
7. Define a NLU and a NLG. List down the different steps involved in the natural language processing (NLP) with suitable examples. [2+6]
8. What do you understand by Perceptron? How can we design a neural network that acts as an XOR gate. [1+8]
9. What are frames and semantic networks? Compare them will suitable examples. [4+3]
10. Write short notes on the following: [2*4]
    - a) Minmax algorithm
    - b) Genetic algorithm

*(Marks checksum 7+8+8+9+8+8+8+9+7+8 = 80.)*

## p8 — 2073 Bhadra, Regular, BEX, CT 78506 (Elective III), IV/II

1. What is Artificial Intelligence? What are the advantages and limitations of Artificial Intelligence over Natural Intelligence? [7]
2. Solve the following puzzle by assigning numeral (0-9) in such a way that each letter is assigned unique digit which satisfy the following addition. [8]

   BASE + BALL = GAMES

3. Compare Greedy Search and A* search along with a simple example. [8]
4. Assume the following facts: [8]
   - John likes all kinds of food.
   - Apples are food.
   - Chicken is food.
   - Anything anyone eats and isn't killed by is food.
   - Bill eats peanuts and is still alive.
   - Sue eats everything bill eats.

   Prove that John likes peanuts using resolution.
5. Why conjuctive normal form is required? Explain all the steps to covert to CNF. Transform following into CNF [2+2+2+3]
   - a) P v (~P ^ Q ^ R)
   - b) Everyone who loves all animals is loved by someone.
6. What is perceptron? How can we design a neural network that acts as an AND gate. [2+6]
7. Explain the different steps involved in the natural language processing (NLP) with suitable block diagram and examples. [7]
8. Explain in details four type of Knowledge Representation Scheme. [8]
9. In a County, 51% of the adults are males and the other 49% are females. One adult is randomly selected for a survey involving credit card usage. Find the prior probability that the selected person is a male. It is later learned that the selected survey subject was smoking a cigar. Also, 9.5% of males smoke cigars, whereas 1.7% of females smoke cigars (based on data from the Substance Abuse and Mental Health Services Administration). Use this additional information to find the probability that the selected subject is a male. [8]
10. Compare the followings: [3x3]
    - a) Mutation versus Crossover
    - b) Induction versus Deduction
    - c) Forward versus Backward Chaining

*(Marks checksum 7+8+8+8+9+8+7+8+8+9 = 80. Q5 a) confirmed by image crop 2026-09-03:
"P v (-P ^ Q ^ R)" with a logical NOT on the second P.)*

## p9 — 2072 Magh, New Back (2066 & Later Batch), BCT, CT 78506 (Elective II as printed), IV/II

**NOTE:** this paper prints Programme **BCT** on a CT 78506 sheet. A DIFFERENT
2072 Magh AI paper (BCT / CT 653) exists in the old scan — see
`CT-653_CT-710_OCR.md` p8. Both are real; the year code "72 Ma" collides.

1. Define an Artificial Intelligence stating the future prominence of the field. Which period was considered as 'AI research failure' period? Why? Write in brief. [7]
2. Consider a Tic-Tac-Toe game playing as a problem. Prepare a brief description of your problem in terms of complete state-space, efficient data structures and goal, which are to be used for a machine to play that game. [7]
3. Though BFS and DFS have some definite way of making search, but still termed as blind search, why? Justify it, comparing with any one informed search technique. [7]
4. Given the following premises: [6+4]

   Bhogendra likes all kinds of food. Oranges are food. Chicken is food. Anything anyone eats and isn't killed by is food. If a person likes a food means that person has eaten it. Jogendra eats peanuts and is still alive. Shailendri eats everything Bhogendra eats.

   Express them in a FOPL, put them into the clause form, and use the resolution to prove that Shailendri likes chicken.
5. What is a semantic net? Draw a sample net about your course AI to demonstrate the knowledge representation features and qualities of semantic net. [7]
6. Explain the working principle of genetic algorithm with some illustrative examples. [7]
7. Explain a multi-layer perceptron working principle with clear statement of related theory. [7]
8. What are the different levels of analysis required in NLP? Justify with one example of each. [6]
9. Differentiate between declarative versus procedural knowledge processing in expert system. [6]
10. Write short notes on [4*4]
    - a) A* search
    - b) Sentence validity
    - c) Learning based on statistics
    - d) Learning rate

*(Marks checksum 7+7+7+10+7+7+7+6+6+16 = 80. Faint scan: Q1's tail, Q2's body and
Q5 were recovered at zoom 5.0 / by image crop on 2026-09-03.)*

## p10 — 2072 Ashwin, Regular, BEX, CT 78506 (Elective III), IV/II

1. What is an Artificial Intelligence, Knowledge and Learning? "Learning is an essential characteristic for intelligent agents". Comment on this statement. [2+2+2+4]
2. Discuss about a Constraints Satisfaction problem (CSP). Solve the following Crypt-arithmetic problem. [8]

       SEND
     + MORE
     -------
      MONEY

3. Explain about depth first and best first search and compare in terms of space and time complexity. [8]
4. Why a Conjuctive normal form is required? Explain all the steps to covert to CNF. Transform "P -> ((Q and ~R) <-> S)" into CNF. [8]
5. After your yearly checkup, the doctor has bed news and good news. The bad news is that you tested positive for a serious disease, and that the test is 99% accurate (i.e, the probability of testing positive given that you have the disease is 0.99, as is the probability of testing negative given that you don't have the disease). The good news is that this is a rare disease, striking only one in 10,000 people. Why is it good news that the disease is rare? What are the chances that you actually have the disease? [8]
6. Differentiate between Supervised and Unsupervised Learning. Clustering fall under which of the above categories? Justify stating algorithms. [2+4]
7. How best attribute is selected in a decision-tree? Select first best attribute of the decision-tree from given sample data. [8]

   | Outlook | Temperature | Humidity | Windy | Play gold (Target variable) |
   |---|---|---|---|---|
   | Rainy | Hot | High | False | No |
   | Rainy | Hot | High | True | No |
   | Overcast | Hot | High | False | Yes |
   | Sunny | Mild | High | False | Yes |
   | Sunny | Cool | Normal | False | Yes |
   | Sunny | Cool | Normal | True | No |
   | Overcast | Cool | Normal | True | Yes |
   | Rainy | Mild | High | False | No |
   | Rainy | Cool | Normal | False | Yes |
   | Sunny | Mild | Normal | False | Yes |
   | Rainy | Mild | Normal | True | Yes |
   | Overcast | Mild | High | True | Yes |
   | Overcast | Hot | Normal | False | Yes |
   | Sunny | Mild | High | True | No |

8. What is the significance role of machine vision help in Artificial Intelligence? Explain how back propagation algorithm works. [3+5]
9. Define a NLU and a NLG? Explain the different ambiguities of Natural Language Processing. [1+7]
10. Write short notes on: [2x4]
    - a) Alpha-beta prunning
    - b) Self Organizing Map (SOM)

*(Marks checksum 10+8+8+8+8+6+8+8+8+8 = 80. Q3 recovered by image crop 2026-09-03.
Q4's connective prints as ">" in the scan's own typography — the paper means "<->".)*

## p11 — 2071 Bhadra, Regular / Back, BEX, CT 78506 (Elective III), IV/II

1. What are main growth areas of Artificial intelligence? Describe with some implementations. Also compare and contrast between belief, hypothesis and knowledge. [4+4]
2. a. You are given two jugs, a 4-gallon one and a 3-gallon one. Neither has any measuring marker on it. There is a pump that can be used to fill the jugs with water. How can you get exactly 2 gallons of water into the 4 gallon jug? Solve it by specifying all steps and properties of problem solving. [4]

   b. Define a production system. What are essential terms or steps of production system? [4]
3. Describe Breadth First Search in detail. Also describe why Breadth First Search is Uninformed or blind search. [8]
4. Define a WFF with its properties. Prove that preposition (A ^ (A->B) -> B) is tautology. [4+4]
5. Define resolution. You are given following statements. [8]
   - a. Ram likes all kinds of food.
   - b. Apples are food.
   - c. Chicken is food.
   - d. Anything anyone eats and is not killed by is food.
   - e. Krishna eats peanuts and is still alive.
   - f. Radha eats everything Krishna eats.

   Prove the statement 'Ram likes peanut' using resolution.
6. Define a frame. What is significance of frame in artificial intelligence? Explain with example. [8]
7. What are the different ways of learning? Describe each in detail. [8]
8. What are features of Hopfield network? How Hopfield network determine active and passive processing unit in network? Clarify with necessary example and illustration. [8]
9. What is an expert system? Describe architecture of expert system with diagram. [8]
10. Define following terms [8]
    - a. Phonetic analysis
    - b. Syntactic analysis
    - c. Semantic analysis
    - d. Pragmatic analysis

*(Marks checksum 8x10 = 80. This paper prints its marks in a plain right-hand column
with no brackets.)*
## p12 — 2082 Bhadra, Regular, BEI, CT 710, IV/I

1. How can you define AI from the dimension of behavioral process and thought process? Using your own assumptions, design PEAS framework for medicine delivery drones. [2+5]
2. In problem solving what is the concept of state space, state, successor function, goal test and path cost? Solve the following crypto arithmetic problem by showing all the steps. [3+5]

   BASE + BALL = GAMES

3. Define the terms admissibility and optimality in the context of A* search. Under what conditions is A* guaranteed to be both admissible and optimal? Provide justification for your answer. [4+5]
4. a) A Bayesian Belief Network (BBN) is used in a medical diagnosis system. The network includes the following binary variables: [7]
   - C: Patient has Cancer (Yes / No)
   - T: Test result is Positive (Yes / No)
   - S: Patient is a Smoker (Yes / No)

   The network structure is: S -> C -> T

   Conditional probabilities are given as:
   P(S=Yes) = 0.3, P(C=Yes | S=Yes) = 0.2, P(C=Yes | S=No) = 0.05,
   P(T=Yes | C=Yes) = 0.9, P(T=Yes | C=No) = 0.1

   Explain how the Bayesian Belief Network enables reasoning under uncertainty in this medical context.

   b) Using given statement prove "Mr. A is a criminal" [6]

   It is crime for a Nepali to sell weapons to enemy of Nepal. Mr. A is an enemy of Nepal. Mr. A has some missiles. Missiles are weapon. Mr. R is a Nepali. If Mr. A has missiles then those missiles were sold to Mr. A are by Mr. R.
5. What are different issues in knowledge representation? Represent the following sentences using semantic net representation. [2+5]

   Tom is a cat. Tom caught a bird. Tom is owned by Sudeep. Tom is ginger in color. Cats like cream. The cat sat on the mat. A cat is a mammal. A bird is an animal. All mammals are animals. Mammals have fur. Sudeep age is 20.
6. Define fuzzy logic and explain how it differs from classical binary logic? Explain Genetic Algorithm with suitable example. [2+6]
7. Design a Hopfield network to store three binary patterns of length 4. Show how to compute the weight matrix and demonstrate the network's ability to recall a pattern from a noisy input. [6]
8. How can ambiguity occur at phonetic, syntactic, semantic and pragmatic levels of natural language processing? Give an example. How syntactic and semantic analysis is done during natural language processing? [3+4]
9. Define Expert System. How does it simulate human reasoning? Explain with example. [2+5]
10. What do you understand about Perception? How can we design a neural network that acts as an XOR gate? [2+6]

*(Marks checksum 7+8+9+13+7+8+6+7+7+8 = 80. NEW paper, not in the old scan.)*

## p13 — 2082 Baishakh, Back, BEI, CT 710, IV/I

1. What is intelligent agent? How can you design an intelligent agent? List down PEAS for self-driving CAR. [2+6]
2. Discuss the steps involved in problem solving. Solve the following crypto-arithmetic problem by stating all the necessary constraints. [2+6]

   BASE + BALL = GAMES

3. What are the drawbacks of greedy best first search method and explain how A* algorithm solves it with a suitable example? [2+6]
4. What is knowledge-based agent? How does it work? Explain with examples. [2+3+2]
5. What are casual networks? Given the following statistics, what is the probability that a woman has cancer if she has positive mammogram result? [2+6]
   - i) One percent of women over 50 have breast cancer.
   - ii) Ninety percent of women who have breast cancer test positive on mammograms.
   - iii) Eight percent of woman will have false positives.
6. When do we use semantic network? Convert the following sentences into semantic network. [2+6]
   - i) Employee is a human.
   - ii) Hari is an employee.
   - iii) Sita is a human.
   - iv) Supervisor is a human.
   - v) Ram is a supervisor.
   - vi) Ram is married to Sita.
   - vii) Ram is supervisor of Hari.
7. When do we use fuzzy logic? Explain the architecture and working mechanism of fuzzy inference system. [2+6]
8. You are stuck in a disaster-prone area of Nepal. Give a specific example how you design expert system in this scenario with its block diagram. Highlight the key components of the designed system. [8]
9. Define a NLU and a NLG. List down the different steps involved in the natural language processing (NLP) with suitable examples. [2+6]
10. Write short notes on: [3x3]
    - a) Adversarial search
    - b) Hopfield network
    - c) Machine vision applications

*(Marks checksum 8+8+8+7+8+8+8+8+8+9 = 80. NEW paper, not in the old scan.
Q8's middle line was recovered at zoom 5.0 on 2026-09-03. The paper's own typo
"casual networks" for "causal networks" is kept.)*

## p14 — 2081 Bhadra, Regular, BEI, CT 710, IV/I

1. If the Turing test is passed, does this show that computer exhibit intelligence? Explain. Compare it with Reverse Turing test with an example. [4+3]
2. What do you understand by constraint satisfaction problem? Solve the following crypto-arithmetic problem by stating all the necessary constraints. [2+6]

       CROSS
     + ROADS
     --------
      DANGER

3. Compare informed and uninformed search. Explain how the Simulated Annealing algorithm to overcome the demerits of hill climbing search. [3+6]
4. Consider the following axioms: [9]
   - Every American who sells weapons to hostile nations is a criminal.
   - Every enemy of America is a hostile.
   - Nono has some missiles.
   - All missiles of Nono were sold by Gorge.
   - Gorge is an American. Nono is a Country.
   - Nono is the enemy of America.
   - Missiles are weapons.

   Prove that "Is Gorge a criminal?" using Resolution by Refutation.
5. Differentiate between forward chaining and backward chaining with examples. [7]
6. Explain different approaches of knowledge representation. Highlight pros and cons of Semantic Nets and Frames. Use them to represent following sentences. [2+6]
   - Figo is a dog.
   - Fido is own by Rohit.
   - Fido is ginger in color.
   - Dog is a mammal.
   - All Mammals are animals.
   - Mammals have fur.
7. When do we use genetic Algorithm? Explain all steps in genetic algorithm with block diagram and operators. [2+6]
8. Define Perception. Justify the statement "Perceptron can work was Linear Classifier" taking reference of Logic gates. [2+6]
9. Define Machine Vision. Discuss the steps involved in Machine Vision with an example. [2+5]
10. Write short notes on: [3x3]
    - a) A* Search
    - b) Kohonen Network
    - c) NLU & NLG

*(Marks checksum 7+8+9+9+7+8+8+8+7+9 = 80; Q4's [9] was confirmed at zoom 5.0.
NEW paper, not in the old scan. The paper's own typos kept: "Figo"/"Fido" in one
list, "Perceptron can work was Linear Classifier".)*

## p15 — 2081 Baishakh, Back, BEI, CT 710, IV/I

1. Define intelligent agent. Explain the factors that are required to pass the Turing Test. [2+6]
2. What is well-defined problem? Solve the following crypto arithmetic problem by showing all the steps. [2+6]

   LOVE + LOVE = HATE

3. Compare the informed and uniformed search techniques. What strategies can be employed to address the issue of local maxima in Hill Climbing Search? [4+4]
4. Define skolemization with example. Consider the following axioms: [2+6]
   - a) Anyone passing his Engineering exams and winning the lottery is happy.
   - b) Anyone who studies or is lucky can pass all his exams.
   - c) Sneha did not study but she is lucky.
   - d) Anyone who is lucky wins the lottery.

   By using resolution refutation, prove that Sneha is happy?
5. What is prior probability and posterior probability? A doctor knows that the disease meningitis causes a patient to have a stiff neck, say, 80% of the time. The doctor also knows some unconditional facts: the prior probability that any patient has meningitis is 1/50000, and the prior probability that any patient has a stiff neck is 1%. Determine the probability of meningitis when a patient has a stiff neck. [2+6]
6. Compare semantic net and frame. How you convert semantic net into frame? Explain with example. [3+5]
7. What are different methods for learning? Explain the steps involved in a genetic algorithm with a flowchart and justify why mutation is important. [3+5]
8. What is perception? Construct a Hebbian Network that performs like AND Gate. [2+6]
9. What is expert system? Explain how inference is performed in expert system? [3+5]
10. Write short notes on: [2x4]
    - a) Fuzzy Logic
    - b) Natural Language Processing

*(Marks checksum 8x10 = 80. ALSO in the old scan — old archive `CT-653_CT-710_OCR.md`
p15. This transcription is from the new scan.)*
## p16 — 2080 Bhadra, Regular, BEI, CT 710, IV/I

Identical to the paper already transcribed in `CT-653_CT-710_OCR.md` **p14**.
Checked question by question against the new scan on 2026-09-03; no differences.
Marks checksum 8x10 = 80.

## p17 — 2080 Baishakh, Back, BEI, CT 710, IV/I

Identical to `CT-653_CT-710_OCR.md` **p16**. Checked on 2026-09-03.
Marks checksum 7+8+8+8+8+7+8+7+7+12 = 80.

## p18 — 2079 Bhadra, Regular, BEI, CT 710, IV/I

Identical to `CT-653_CT-710_OCR.md` **p17**. Checked on 2026-09-03.
The new scan clips Q3 at the page edge; the old archive has it in full:
"Different between Depth first search and Breadth first search with their
performance criteria. [7]".
Marks checksum 7+8+7+8+7+8+8+8+7+12 = 80.
## p19 — 2082 Kartik, Back, BCT, CT 653, III/II

1. Define Artificial Intelligence. Design the PEAS information Automated Robot in a manufacturing plant. [2+3]
2. What are criteria for defining problem? Solve the following crypto-arithmetic algorithm: [2+6]

   BASE + BALL = GAMES

3. What do you mean by Searching and what are the types of Search methods? What are the drawbacks of Min-Max algorithm and explain how Alpha-Beta pruning algorithm solves it with a suitable example? [3+6]
4. a) Use resolution solve following problem: The law says that it is a crime for an American to sell weapons to hostile nations. The country Nono, an enemy of America has some missiles, and all of its missiles were sold to it by Colonel West, who is American. Prove That Col. West is criminal. [8]

   b) Define production system. Define and differentiate forward and backward chaining. [2+4]
5. Define term frame. Convert the following sentences into semantic network. Cat is a mammal. Cat has fur. Mammal has vertebra. Mammal is an animal. Bear is a mammal. Bear has fur. Whale is a mammal. Whale lives in water. Fish is an animal 10. Fish lives in water. [1+6]
6. What is fuzzy logic? Explain the steps involved in genetic algorithm with examples. [2+6]
7. Below is a neural network with weights a, b, c, d, e, and f. The input are x1 and x2. The first hidden layer computes r1 = max(c.x1 + e.x2, 0) and r2 = max(d.x1 + f.x2, 0). The second hidden layer and third layer computes s1, s2 and y using sigmoid activation function. Suppose the network has inputs x1 = -1 and x2 = -1. The weight values are a = 1, b = 1, c = 4, d = 1, e = 2 and f = 2. Perform forward propagation. And update weight for second hidden layer for a and b. [8]
   *(FIGURE: the two-input / two-hidden-layer network, arcs labelled a-f, nodes r1, r2, s1, s2, y. Needs a crop.)*
8. Define term expert system and expert system Shells. What are the characteristics that problem possesses are solved by expert system? Explain with example. [2+2+3]
9. Explain the McCulloch-Pitts model of a neuron with a diagram. Explain with example how to choose best activation function in particular project? [4+3]
10. What are the problem associated with NLP? List down the different steps involved in the natural language processing with suitable example. [2+5]

*(Marks checksum 5+8+9+14+7+8+8+7+7+7 = 80. Q6 was blank in the page OCR and was
read from an image crop on 2026-09-03. Q5's "Fish is an animal 10." is the paper's
own stray "10." — kept verbatim. NEW paper.)*

## p20-21 — 2081 Chaitra, Regular, BCT, CT 653, III/II

1. How you define Artificial Intelligence (AI). Explain AI applications in different areas as problem solving tool. [2+4]
2. Explain steps of problem solving with suitable example. Solve the following crypto-arithmetic algorithm SWIM + WEAR = RELAX. [3+6]
3. Explain A* algorithm in following figure where starting node is S and destination is G. (Note: Information in the node represents cost required to reach the goal and information in the connecting link represents cost from one node to the other. [8]
   *(FIGURE: the S-to-G cost graph. Needs a crop.)*
4. a) Assume the following facts: [8]

   Every child loves Santa. Everyone who loves Santa loves any reindeer. Rudolph is a reindeer, and Rudolph has a red nose. Anything which has a red nose is weird or is a clown. No reindeer is a clown. Scrooge does not love anything which is weird. Using Resolution Refutation method derive the following conclusion: Scrooge is not a child.

   b) What is CNF? Explain rule of inference along with example. [2+3]
5. Define term semantic net. Represent the following sentences using semantic net representation. [2+6]

   Tom is a cat. Tom caught a bird. Tom is owned by Sudeep. Tom is ginger in color. Cats like cream. The cat sat on the mat. A cat is a mammal. A bird is an animal. All mammals are animals. Mammals have fur. Sudeep age is 20.
6. Name and describe the main features of Genetic Algorithms along with example [7]
7. Define Expert System with example. Explain the limitations of Expert System. [4+3]
8. What is the role of activation function in ANN? Explain the McCulloch-Pitts model of a neuron with a diagram. [3+4]
9. Below is a neural network with weights a, b, c, d, e, and f. The input are x1 and x2. The first hidden layer computes r1 = max(c.x1 + e.x2, 0) and r2 = max(d.x1 + f.x2, 0). The second hidden layer and third layer computes s1, s2 and y using sigmoid activation function. Suppose the network has inputs x1 = -1 and x2 = -1. The weight values are a = 1, b = 1, c = 4, d = 1, e = 2 and f = 2. Perform forward propagation. And update weight for second hidden layer for a and b. [8]
   *(FIGURE: same network as p19 Q7. One crop serves both.)*
10. What are the problem associated with NLP? List down the different steps involved in the natural language processing with suitable example [2+5]

*(Marks checksum 6+9+8+13+8+7+7+7+8+7 = 80. NEW paper. Q9 here and Q7 on p19
are the same question, printed with the same figure.)*
## p22 — 2081 Ashwin, Back, BCT, CT 653, III/II

1. What is intelligent agent? Do we need PEAS for designing an intelligent agent? If so, define PEAS and provide the PEAS information for Taxi Driver Agent and Automated Robot in a manufacturing plant. [1+5]
2. List down the characteristics of well-defined problem. [8]

   You are given two jugs, a 5-litre one and a 2-litre one. Neither has any measuring markers on it. There is a pump that can be used to fill the jugs with water. You are required to measure exactly 1 liter of water. Is this well-defined problem? Justify your argument and list all the attributes to design an intelligent agent. Solve this problem by specifying states and the operations used.
3. List down the approaches for evaluating searching methods. What are the drawbacks of Min-Max algorithm and explain how Alpha-Beta pruning algorithm solves it with a suitable example? [2+6]
4. What do you mean by Forward and Backward Chaining? The law says that it is a crime for an American to sell weapons to hostile nations. The country Nono, an enemy of America has some missiles, and all of its missiles were sold to it by Colonel West, who is American. Prove That Col. West is criminal using forward chaining. [2+6]
5. What are the approaches for measuring uncertainty? [2+6]

   1% of people have a certain genetic defect. 90% of tests for the gene detect the defect (true positives). 10% of the tests are false positives.
   - a) What might be the probability of getting the genetic defect result?
   - b) If a person gets a positive test result, what are the odds they actually don't have the genetic defect?
6. What are Frames and Sematic Network? Convert the following sentences into FOPL and represent using semantic network. [2+6]
   - i) Ram is a person.
   - ii) Person is an animal.
   - iii) Ram likes Jhilke.
   - iv) Jhilke is a cat.
   - v) Cat eats fish.
   - vi) Cat is an animal.
   - vii) fish is an animal.
7. When shall we use genetic algorithm? Explain with appropriate example. Discuss about the steps in genetic algorithm including selection, crossover and mutation operations. [3+5]
8. You are hired by a company to work on product based on a Nepali Language. What are challenges/issues associated with NLP? List them with appropriate examples and relate these with Nepali Language. What are your plans to mitigate these challenges while working in the company? [8]
9. What is Machine Vision? List down the steps involved in Machine Vision by giving suitable example. [2+4]
10. Write Short notes on: [3x4]
    - a) Fuzzy Logic
    - b) Learning in Neural Network
    - c) Expert System

*(Marks checksum 6+8+8+8+8+8+8+8+6+12 = 80. NEW paper. The paper's own typo
"Sematic Network" is kept.)*

## p23-24 — 2080 Chaitra, Regular, BCT, CT 653, III/II

1. Can machine think? Explain your stance with appropriate reasons. Relate it with Turing Test and Reverse Turing Test. [2+4]
2. What do mean by Constraints Satisfaction Problem? List all the constraints and solve the following crypto-arithmetic problem: EAT + THAT = APPLE [2+5]
3. How A* search overcomes problem associated with Greedy Best First Search? Using following figure and table where starting node is S and destination is G, compare the result of A* algorithm with greedy search. [3+4+3]

   | From | Cost |
   |---|---|
   | S | 15 |
   | A | 10 |
   | B | 12 |
   | C | 5 |
   | D | 4 |
   | E | 2 |
   | F | 1 |
   | G | 0 |

   (Note: Table gives the cost required to reach the goal and information in the connecting link represents cost from one node to the other.)
   *(FIGURE: the S-to-G graph with edge costs. Needs a crop.)*
4. List down the steps for converting to CNF and proof by resolution refutation. Convert the following sentences into FOPL and answer "Did Curiosity kill the cat" by resolution refutation. [3+5]
   - a) Everyone who loves all animals is loved by someone.
   - b) Anyone who kills an animal is loved by no one.
   - c) Jack loves all animals.
   - d) Either Jack or Curiosity killed the cat.
5. Discuss about the different approaches knowledge representation. How do you make choice among these approaches? Is it possible to evaluate the knowledge representation? List down any issues associated with it. [2+2+2+2]
6. When shall we use Fuzzy Logic? Explain with appropriate example. What are the steps of major steps for developing system based on Fuzzy logic? [2+5]
7. What is Prior Probability and Posterior Probability and show how these probabilities are used in Bayes Theorem. Is there any connection between Belief Network and Bayes Theorem? Justify with an example. [3+5]
8. You are hired by a company to develop a Nepali Chatbot System. What are the knowledge bases that is required to develop the system? List down the different steps involved in the development of this Nepali Language based NLP tool with suitable block diagram and examples. [2+6]
9. You need to work as a Knowledge Engineer for a company in developing expert system for Disease Diagnosis. Draw a block diagram and highlight the major steps for development of this expert system. [6]
10. Write Short notes on: [3x4]
    - a) Forward chaining and Backward chaining
    - b) Hopfield Neural Network
    - c) Machine Vision

*(Marks checksum 6+7+10+8+8+7+8+8+6+12 = 80. NEW paper. Q3's stem was recovered
by image crop on 2026-09-03.)*
## p25 — 2080 Ashwin, Back, BCT, CT 653, III/II

1. What is Artificial Intelligence? Explain different types of Intelligent Agents with examples. [2+6]
2. Define term well defined problem. Solve the following crypto arithmetic problem by showing all the steps. [2+6]

   ONE + ONE + TWO = FOUR

3. Why is searching important in problem solving? Differentiate between Depth first search and Breadth first search with their performance criteria. [2+6]
4. What are different issues in knowledge representation? Discuss the importance of frame in knowledge representation with suitable example. [3+5]
5. List the rules of inference. Convert the following into FOPL and prove using Resolution Refutation System. "All people who are not poor and are smart are happy. Those people who can read are not stupid. John can read and is wealthy. Happy people have exciting lives. Can anyone be found with an exciting life?" [3+5]
6. When do we need hopfield Neural Network? Make a comparision between feed forward network and hopfield Network. [3+5]
7. How reasoning is done in uncertainty? Three factories produce light bulbs to supply the market. Factory A produces 20%, 50% of the tools are produced in factories B and 30% in factory C. 2% of the bulbs produced in factory A, 5% of the bulbs produced in factory B and 3% of the bulbs produced in factory C are defective. A bulb is selected at random in the market and found to be defective. What is the probability that this bulb was produced by factory B? [3+5]
8. Define Machine learning. What is Fuzzy logic? Explain Fuzzy inference with suitable example. [1+2+5]
9. Compare expert systems and human experts. Explain each point with suitable practical examples. [8]
10. What is machine vision? Create a senario where we require Machine vision. List down the steps how you solve the above problem. [2+6]

*(Marks checksum 8x10 = 80. NEW paper. The paper's own typos kept: "comparision",
"senario", and Q7's "50% of the tools" where it means bulbs.)*

## p26 — 2079 Chaitra, Regular, BCT, CT 653, III/II

Identical to the paper already transcribed in `CT-653_CT-710_OCR.md` **p13**.
Checked question by question against the new scan on 2026-09-03; no differences.
Q5 is clipped in the new scan's page OCR — the old archive has it in full:
"Why CNF is necessary? 'Everyone who loves all animals are loved by someone'
represent this statement in FOPL and explain all the steps involved to convert it
into CNF. [2+6]".
Q3's game tree is already cropped to `AI/images/ai_79ch_minmax.png`.
Marks checksum 8x10 = 80.

## p27 — 2079 Ashwin, Back, BCT, CT 653, III/II

1. What is knowledge and learning? Why they are important? Explain the factors that are require to pass the Turing test. [2+2+4]
2. What is constraint satisfaction problem? Solve the following crypto-arithmetic algorithm: [2+6]

   BASE + BALL = GAMES

3. On what basis can we evaluate the search algorithms? Explain. What are the approaches for Depth First Search and Depth Limit Search? Explain. [4+4]
4. Assume the following facts: [7]
   - a) Steve only likes easy courses.
   - b) Science courses are hard.
   - c) All the courses in basket weaving department are easy.
   - d) BK301 is a basket weaving course.

   Prove that Steve likes BK301 course using Resolution Refutation Method.
5. Why probabilistic reasoning is important in the AI? When do we use Bayesian Network? Explain. [3+6]
6. What are the different approaches for knowledge representation? List down the essential properties and issues of the knowledge representation system. [4+2+2]
7. What is Fuzzy logic? When do we use it? Explain the steps with suitable example. [1+2+5]
8. What is perceptron? Is single perceptron sufficient to realize a network behaving as XOR gate? Justify. [1+8]
9. Explain different steps involved in NLP. Why NLP is hard? Explain [5+2]
10. What is machine vision? What are the different steps involved? List down its applications. [1+5+2]

*(Marks checksum 8+8+8+7+9+8+8+9+7+8 = 80. NEW paper.)*
## p28-29 — 2079 Jestha, Back, BCT, CT 653, III/II

1. Define intelligent agent. Explain different types of intelligent agents and their interaction with environments alongwith appropriate examples. [1+6]
2. Discuss about Constraints Satisfaction Problem (CSP). Solve the following Crypt-arithmetic problem. [1+6]

       BASE
     + BALL
     -------
      GAMES

3. Differentiate between depth first search and breadth first search with an example. [7]
4. a) Assume the following facts: [6]
   - (i) Horses, cows, pigs are mammals.
   - (ii) An offspring of a horse is a horse.
   - (iii) Bluebeard is a horse.
   - (iv) Bluebeard is Charlie's parent.
   - (v) Offspring and parent are inverse relations.
   - (vi) Every mammal has a parent.

   Prove Charlie is a horse using resolution refutation.

   b) Why Conjuctive normal form is required? Explain all the steps to covert to CNF. Transform each of the following sentences into CNF. [2+2+4]
   - (i) ~(P & Q) v (P v S) -> R
   - (ii) P -> ((Q & ~R) <-> S)
5. What is perceptron? Can we design a neural network that acts as logic gates? Explain with an example. [1+6]
6. Differentiate between NLU and NLG. List down the different steps involved in the natural language processing (NLP) with suitable examples. [1+6]
7. Write short notes on the following: [3x5]
   - a) A* Search
   - b) Semantic Network and Frame
   - c) Self Organizing Map (SOM)
8. a) "Learning is an essential characteristic for intelligent agents." Comment on this statement. Differentiate between Supervised and Unsupervised Learning. [4+4]

   b) How best attribute is selected in a decision-tree? Select the root attribute of the decision-tree from given sample data. [1+7]

   | Outlook | Temperature | Humidity | Windy | Play cricket (Target variable) |
   |---|---|---|---|---|
   | Rainy | Hot | High | False | Yes |
   | Rainy | Hot | High | True | No |
   | Overcast | Hot | High | False | Yes |
   | Sunny | Mild | High | False | Yes |
   | Sunny | Cool | Normal | False | Yes |
   | Sunny | Cool | Normal | True | No |
   | Overcast | Cool | Normal | True | Yes |
   | Rainy | Mild | High | True | No |
   | Rainy | Cool | Normal | False | Yes |
   | Sunny | Mild | Normal | False | Yes |
   | Rainy | Mild | Normal | True | No |
   | Overcast | Mild | High | True | Yes |
   | Overcast | Hot | Normal | False | Yes |
   | Sunny | Mild | High | True | No |

*(Marks checksum 7+7+7+6+8+7+7+15+8+8 = 80. NEW paper. NOTE this decision-tree
table differs from the CT 78506 "Play golf" one: the target is "Play cricket" and
rows 1, 8 and 11 carry different labels.)*

## p30 — 2078 Chaitra, Regular, BCT, CT 653, III/II

1. What are intelligent agents and how can we design intelligent agent? Explain with examples on relevance to PEAS framework. [4+4]
2. What is well defined problem? Solve the following crypto-arithmetic problem by defining it. [2+6]

   TWO + TWO = FOUR

3. Why is searching important in problem solving? What are the drawbacks of greedy best-first search and how A* search technique is used to solve it. Explain with example. [2+7]
4. Define horn clause with example. Consider the following axioms: [3+3]
   - i) Every child love Santa.
   - ii) Everyone who loves Santa loves any reindeer.
   - iii) Rudolph is a reindeer, and Rudolph has a red nose.
   - iv) Anything which has a red nose is weird or is a clown.
   - v) No reindeer is a clown.
   - vi) Scrooge does not love anything which is weird.

   Represent these axioms in a predicate calculus and then convert each formula to CNF. List down the rules of inference. When can we use these rules? Explain.
5. Explain how statistical reasoning aids in inference and reasoning in light of Bayes theorem. At a certain University, 5% of men are over 6 feet tall and 2% of women are 6 feet tall. 60% of students are female. If a student is selected at a random from among all those over six feet tall, what is the probability that the selected students is woman? [3+5]
6. Explain frame and Semantic Net with example. List down their advantages and disadvantages. [4+4]
7. List down the algorithms inspired by biological phenomena and social behaviors. Explain the learning process in Genetic Algorithm with suitable block diagram. [2+6]
8. Using Hebbian learning algorithm construct a neural network that behaves as an AND gate. Is hebbian learning supervised method? Justify. [6+3]
9. What are expert systems? Explain the architecture of expert system with suitable block diagram. Highlight the advantages and disadvantages of expert system. [1+4+3]
10. What is natural language understanding and natural language generation? Briefly list down the steps. Discuss the issues related with NLP. [2+4+2]

*(Marks checksum 8+8+9+6+8+8+8+9+8+8 = 80. NEW paper. The scan is speckled — a few
letters OCR'd as "inferenct", "studert", "corstruct", "nethod", "he", "undzrstanding";
those are scan artefacts, not the paper's own typos, and are corrected above.)*
## p31 — 2078 Poush, Back, BCT, CT 653, III/II

1. Compare human intelligence and machine intelligence. Discuss some applications of Artificial Intelligence. [3+5]
2. Discuss about Constraints Satisfaction Problem (CSP). Solve the following Crypt-arithmetic problem. [2+6]

   FORTY + TEN + TEN = SIXTY

3. Justify how A* algorithm provides optimum solution compared with greedy search algorithm. [8]
4. Explain forward chaining giving suitable example. [8]
5. Assume the following facts: [8]
   - a. Horses, cows, pigs are mammals.
   - b. An offspring of a horse is a horse.
   - c. Bluebeard is a horse.
   - d. Bluebeard is Charlie's parent.
   - e. Offspring and parent are inverse relations.
   - f. Every mammal has a parent

   Prove Charlie is a horse using resolution refutation
6. What are Frames and Semantic Net? Convert the given sentences in semantic Net: [2+6]
   - A person is a mammal.
   - Sandeep Lamichane is a person.
   - Person has nose.
   - Sandeep Lamichane is in Nepalese cricket team.
   - Uniform color of Sakti Gauchan is Red/Blue.
7. What is Machine Learning? Discuss about Supervised, Unsupervised and Reinforcement Learning with appropriate examples. [2+6]
8. What are problems of natural language understanding? Discuss the steps of NLP. [3+5]
9. Define Perceptron and multilayered perceptron. Design a neural network which acts as AND gate. [2+2+4]
10. Write short notes on the following: [2x4]
    - a) Adversial Search
    - b) Fuzzy logic

*(Marks checksum 8x10 = 80. NEW paper. The paper's own spelling "Adversial",
"Lamichane", "Sakti Gauchan" is kept.)*

## p32-33 — 2078 Baishakh, Back, BCT, CT 653, III/II

1. List down disadvantages of AI? What is the importance of the Turing Test in Artificial Intelligence? What are the applications of AI? Explain. [2+2+4]
2. What do you understand by Constraint satisfaction problem? Solve the given Crypt-arithmetic problem: [2+6]

        T E N
        T E N
    + F O R T Y
    -------------
      S I X T Y

3. Explain A* search method using a suitable example. Discuss the drawbacks of Hill Climbing Algorithm. [6+2]
4. Assume the following facts: [8]
   - (i) Cow, Buffalo, Bull are mammals.
   - (ii) An offspring of a Cow is Cow.
   - (iii) Kali is a Cow.
   - (iv) Kali is Taarey's parent.
   - (v) Offspring and parent are inverse relations.
   - (vi) Every mammal has a parent.

   By using resolution refutation method, prove that Taarey is a Cow.
5. What do you understand by Bayesian Network? For the given Bayesian network below, find the probability of grass being wet when the weather is cloudy, there is some sprinkler but no rain i.e. C = True, S = True, R = False and W = True. [2+6]

   *(FIGURE: the Cloudy -> Sprinkler / Rain -> Wet Grass network with its CPTs.
   Values confirmed by image crop 2026-09-03:*
   P(C) = 0.6;
   P(S|C): T .10, F .50;
   P(R|C): T .80, F .20;
   P(W|S,R): T T .99, T F .90, F T .90, F F .01.
   *Needs a crop for the diagram itself.)*
6. Differentiate between frames and semantic nets with an example. Why semantics nets and frames are important in AI? [6+2]
7. What is Machine Learning? Explain learning framework with suitable block diagram. [2+6]
8. What is perception? Construct a Hebbian network that performs like an AND gate. [1+7]
9. Explain the ambiguity in NLP. Discuss the different steps involved during NLP. [2+6]
10. Write short notes on: [2x4]
    - a) Supervised vs Unsupervised Learning
    - b) Minmax algorithm

*(Marks checksum 8x10 = 80. NEW paper.)*
## p34 — 2077 Chaitra, Regular, BCT, CT 653, III/II

1. Define Artificial Intelligence (AI). When is a machine said to have passed the Turing Test? Discuss two fields of application of AI. [2+3+3]
2. What do you understand by Production system problem? Solve the following crypto arithmetic problem. [2+6]

   WRONG + WRONG = RIGHT

3. List out the disadvantages of MIN-MAX algorithm for Game playing and explain how Alpha-beta pruning helps to overcome the limitation of MIN-MAX algorithm with an example. [2+6]
4. It is a crime for an American to sell weapons to hostile nations. Nono has some missiles. All the missiles owned by Nono were sold to it by Colonel West. Missiles are weapons. An enemy of America counts as hostile. Colonel West is an American. The country Nono, is an enemy of America. Prove that Colonel West is a criminal by using FOPL based Resolution Refutation Method. [8]
5. What is rule-based reasoning? Explain with an example. How Bayes theorem used in belief network? [2+6]
6. What do you mean by Conceptual Dependency? Explain how knowledge is represented using scripts. [3+5]
7. Explain all the steps in the genetic algorithm with block diagram and operators. [8]
8. What is neural network? Show that a single neuron cannot implement XOR gate. [2+6]
9. Draw the block diagram of an expert system and briefly explain each component. List the benefits of using expert system? [6+2]
10. Write short notes on: [2x4]
    - a) Hill climbing problems
    - b) Fuzzy learning

*(Marks checksum 8x10 = 80. NEW paper.)*

## p35 — 2076 Baishakh, Back, BCT, CT 653, III/II

**Header prints "2076 Baisakh".**

1. Define Artificial Intelligence. Justify that "system that think rationally and act rationally." is part of Artificial Intelligence. [8]
2. Solve following crypto-arithmetic problem. [8]

   SEND + MORE = MONEY.

   Assign different decimal digit to different letters. Explain the steps followed for the solution.
3. Discuss about alpha-beta purning algorithm. Find the value of min max value using this concept in the following tree. [4+4]
   *(FIGURE: a MAX-at-top / MIN game tree with numbered leaves. Needs a crop.)*
4. List down the rule for Inference. Consider the following axioms. [2+8]
   - All hounds howl at night.
   - Anyone who has any cats will not have any mice.
   - Light sleepers do not have anything which howls at night.
   - John has either a cat or a hound.

   Prove: "If John is a light sleeper, then John does not have any mice." By using resolution refutation.
5. Define a semantic network and frames with an example. List advantages and limitations of both. [6+2]
6. What is machine learning? Explain learning by analogy with example. [2+6]
7. What is McCulloch/Pitts neuron? Can this neuron be trained to represent EX-OR gate? Justify and propose neural network model. [10]
8. What is an expert system? Explain the components of an expert system. [1+7]
9. Write short notes on: [3x4]
   - a) Boltzman Machine
   - b) Conjuctive Normal Form
   - c) A* Algorithm

*(Marks checksum 8+8+8+10+8+8+10+8+12 = 80 over NINE questions, not ten.
NEW paper. Q5 was recovered at zoom 5.0 on 2026-09-03. The paper's own spellings
"purning", "Boltzman", "Conjuctive" are kept.)*

## p36 — 2075 Bhadra, Regular, BCT, CT 653, III/II

**Exam cell is heavily inked; read as "Regular" from an image crop 2026-09-03.**

1. What is an intelligent agent? How does learning agent work? [8]
2. What do you understand about well defined problems? Explain about problems that can be solved using production rules with an example. [2+6]
3. Discuss about the evaluation criteria for search algorithm. State the problems in hill climbing search algorithm. [4+4]
4. Why CNF is necessary? "Everyone who loves all animals are loved by someone" represent this statement in FOPL and explain all the steps involved to convert it into CFN. [2+6]
5. What is knowledge representation? How semantic network is used to represent knowledge? [2+6]
6. What do you understand by swarm intelligence? Suppose chromosomes are of the form x = a b c d e f g h with a fixed length of eight genes. Each gene can be any digit between 0 and 9. Let the fitness of individual x be calculated as: [2+8]

   f(x) = (a+b) - (c+d) + (e+f) - (g+h)

   and let the initial population consist of four individuals with the following chromosomes.

   **DEFECT IN THE PAPER:** the sentence ends there. No chromosome list is printed —
   the page runs straight on to Q7. Confirmed by image crop 2026-09-03. Same class of
   defect as Data Mining 2081 Baishakh Q4b.
7. What is Natural Language Processing (NLP)? Discuss the different steps in NLP with suitable examples. Also list down major issues in NLP. [6+2+2]
8. Explain Hopfield network with an example. [8]
9. Write short notes on: [3x4]
   - i) Predicate logic
   - ii) Unsupervised learning
   - iii) Breadth first vs depth first search

*(Marks checksum 8+8+8+8+8+10+10+8+12 = 80 over NINE questions. NEW paper.
Q4's "CFN" is the paper's own typo for CNF.)*
## p37-p48 — the twelve CT 653 papers that were already transcribed

Pages 37-48 of the new scan reproduce, one paper per page, the twelve oldest
CT 653 papers. Every one of them is already transcribed verbatim in
`CT-653_CT-710_OCR.md`; **use that file for their question text.**

| New scan | Paper | Exam | Old archive |
|---|---|---|---|
| p37 | 2075 Baishakh | Back | p12 |
| p38 | 2074 Bhadra | Regular | p11 |
| p39 | 2073 Magh | New Back (2066 & Later Batch) | p10 |
| p40 | 2073 Bhadra | Regular | p9 |
| p41 | 2072 Magh | New Back (2066 & Later Batch) | p8 |
| p42 | 2072 Ashwin | Regular | p7 |
| p43 | 2071 Magh | New Back (2066 & Later Batch) | p6 |
| p44 | 2071 Bhadra | Regular / Back | p5 |
| p45 | 2070 Magh | New Back (2066 & Later Batch) | p4 |
| p46 | 2070 Bhadra | Regular | p3 |
| p47 | 2069 Poush | New Back (2066 & Later Batch) | p2 |
| p48 | 2069 Bhadra | Regular (2066 & Later Batch) | p1 |

Verified on 2026-09-03 with `tools/ai_dupcheck.py`, which scores each old-archive
paper's vocabulary against the new page's raw OCR. All twelve scored 0.77-1.00;
the two lowest (p48 = 0.77, p43 = 0.85) are OCR word-merging on a noisy scan, not
different papers — p48 was read back in full to confirm.

One difference worth recording: the new scan's page OCR reads 2069 Bhadra Q3 as
**(6)** marks. It is **[9]** — the old archive is right, and only [9] makes the
paper add to 80 (7+7+9+10+7+4+6+8+8+6+8).

The 2079 Chaitra (p26), 2081 Baishakh (p15), 2080 Bhadra (p16), 2080 Baishakh
(p17) and 2079 Bhadra (p18) papers are likewise already in the old archive; see
their entries above.

**Consequence: the new scan is a strict superset of `AI/CT-653_69-75_79_CT-710_70-81.pdf`.**
Unlike DSAP and Wireless, the old AI scan holds no paper of its own.
