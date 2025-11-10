"""Test cases for German language questions and conditions"""
import pytest
from src.models.checklist import (
    Question,
    Condition,
    ChecklistTemplate,
    QuestionType,
    ConditionType
)


class TestGermanLanguageSupport:
    """Test German language questions and conditions"""
    
    def test_german_question_creation(self):
        """Test creating a question in German"""
        question = Question(
            question="Was ist das Startdatum des Vertrags?",
            question_type=QuestionType.TEXT,
            context="Suchen Sie nach Daten im Vertragskopf oder im Abschnitt 'Bedingungen'",
            required=True,
            order=0
        )
        
        assert question.question == "Was ist das Startdatum des Vertrags?"
        assert question.context == "Suchen Sie nach Daten im Vertragskopf oder im Abschnitt 'Bedingungen'"
        assert question.question_type == QuestionType.TEXT
    
    def test_german_condition_creation(self):
        """Test creating a condition in German"""
        condition = Condition(
            condition="Vertrag enthält eine Kündigungsklausel",
            condition_type=ConditionType.CUSTOM,
            context="Prüfen Sie, ob es einen Abschnitt gibt, der die Vertragskündigung oder den vorzeitigen Ausstieg behandelt",
            required=True,
            order=0
        )
        
        assert condition.condition == "Vertrag enthält eine Kündigungsklausel"
        assert condition.context == "Prüfen Sie, ob es einen Abschnitt gibt, der die Vertragskündigung oder den vorzeitigen Ausstieg behandelt"
        assert condition.condition_type == ConditionType.CUSTOM
    
    def test_german_checklist_template(self):
        """Test creating a complete German checklist template"""
        questions = [
            Question(
                question="Was ist das Startdatum des Vertrags?",
                question_type=QuestionType.TEXT,
                context="Suchen Sie nach Daten im Vertragskopf",
                required=True,
                order=0
            ),
            Question(
                question="Wie hoch ist der Gesamtwert des Vertrags?",
                question_type=QuestionType.TEXT,
                context="Suchen Sie nach Geldbeträgen im Preis- oder Zahlungsabschnitt",
                required=True,
                order=1
            ),
            Question(
                question="Wer sind die Vertragsparteien?",
                question_type=QuestionType.TEXT,
                context="Identifizieren Sie alle genannten Parteien im Vertrag",
                required=True,
                order=2
            )
        ]
        
        conditions = [
            Condition(
                condition="Vertrag enthält eine Kündigungsklausel",
                condition_type=ConditionType.CUSTOM,
                context="Prüfen Sie auf Kündigungsbestimmungen",
                required=True,
                order=0
            ),
            Condition(
                condition="Vertrag enthält Haftungsausschlüsse",
                condition_type=ConditionType.CUSTOM,
                context="Suchen Sie nach Haftungsbeschränkungen oder Ausschlüssen",
                required=True,
                order=1
            ),
            Condition(
                condition="Zahlungsbedingungen sind klar definiert",
                condition_type=ConditionType.CUSTOM,
                context="Überprüfen Sie, ob Zahlungsfristen und -methoden spezifiziert sind",
                required=True,
                order=2
            )
        ]
        
        template = ChecklistTemplate(
            name="Vertragsüberprüfungs-Checkliste",
            description="Checkliste zur Überprüfung von Vertragsunterlagen",
            questions=questions,
            conditions=conditions
        )
        
        assert template.name == "Vertragsüberprüfungs-Checkliste"
        assert len(template.questions) == 3
        assert len(template.conditions) == 3
        assert all(q.question for q in template.questions)
        assert all(c.condition for c in template.conditions)
    
    def test_mixed_language_support(self):
        """Test that system can handle mixed English and German content"""
        template = ChecklistTemplate(
            name="Mixed Language Template",
            description="Template with both English and German",
            questions=[
                Question(
                    question="What is the contract start date?",
                    question_type=QuestionType.TEXT,
                    required=True,
                    order=0
                ),
                Question(
                    question="Was ist das Enddatum des Vertrags?",
                    question_type=QuestionType.TEXT,
                    required=True,
                    order=1
                )
            ],
            conditions=[
                Condition(
                    condition="Contract includes termination clause",
                    condition_type=ConditionType.CUSTOM,
                    required=True,
                    order=0
                ),
                Condition(
                    condition="Vertrag enthält Datenschutzbestimmungen",
                    condition_type=ConditionType.CUSTOM,
                    required=True,
                    order=1
                )
            ]
        )
        
        assert len(template.questions) == 2
        assert len(template.conditions) == 2
