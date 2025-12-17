from core import XAI

xai = XAI()

text = """
Modern classrooms often emphasize technical competence, yet many students still struggle with basic collaboration skills. This challenge becomes visible when group projects break down because individuals feel unheard or undervalued. Teachers often interpret this as a lack of motivation, but the root cause is usually a lack of structured opportunities to practice empathy and communication.

One effective approach is to encourage students to explain their reasoning rather than defend their conclusions. When a student articulates how they reached an answer, peers begin to see the value in process-oriented thinking. This reduces conflict and fosters a healthier intellectual environment.

Another strategy involves rotating group roles. When students regularly switch between tasks—such as researcher, scribe, presenter, and evaluator—they develop a broader understanding of how collaborative work functions. It also prevents one individual from dominating the group dynamic.

Teachers can also model productive disagreement. Instead of correcting a student outright, they can pose counterquestions that highlight gaps in reasoning. This shows students that disagreement can lead to clarity rather than confrontation.

Regular reflection sessions amplify these benefits. After each project, students can write short notes about what went well and what created tension. This metacognitive step helps them recognize patterns in their behavior.

Importantly, collaboration skills do not have to be tied only to academic tasks. Shared non-academic activities—such as maintaining a class garden, organizing a small event, or creating artwork—serve as low-pressure environments where students practice cooperation naturally.

Classroom climate plays a major role as well. Students are more willing to collaborate when they feel psychologically safe and respect one another’s contributions. A simple greeting ritual at the beginning of class can set the tone for the entire day.

Technology can either help or hinder these efforts. Collaborative digital tools make it easier for reserved students to contribute because they have more time to formulate their thoughts. However, overreliance on digital communication reduces face-to-face interaction, which remains essential for building trust.

Teachers should also consider linguistic and cultural diversity within the classroom. A strategy that works well for native speakers may unintentionally exclude multilingual learners. Small adjustments—such as providing sentence starters or allowing more wait time—can make group work significantly more inclusive.

Assessment systems must align with these goals. If grading focuses only on the final product, students will see little value in the collaborative process. Rubrics that reward communication, equitable participation, and constructive feedback create stronger incentives.

Family engagement enhances collaboration skills outside of school hours. When parents understand the purpose of group activities, they can reinforce these skills at home through shared chores or family discussions.

Schools should also provide professional development for teachers. Many educators were never explicitly taught how to facilitate group dynamics, yet they are expected to manage them effectively. Short workshops can introduce practical tools such as conflict-mapping, turn-taking strategies, and equitable questioning.

Finally, patience is crucial. Collaboration skills are not mastered in a few weeks; they evolve gradually through recurring practice and reflection. Schools that remain committed to the process eventually see improvements not only in group work but also in academic performance and overall classroom culture.

In the long run, teaching students how to collaborate is as important as teaching them mathematics or reading. These skills shape their relationships, careers, and ability to contribute meaningfully to society.
"""
try:
    explanations = xai.shap_explainer(text)
except Exception as e:
    print(f"Got error {e} during SHAP explanation")