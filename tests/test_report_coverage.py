import unittest
from unittest.mock import patch
from scripts import report_coverage

class CoverageReportTests(unittest.TestCase):
    def test_current_reviews_and_linked_syllabi_are_distinct_from_legacy(self):
        rows=[{'id':'A','name':'Alpha'},{'id':'B','name':'Beta'}]
        database={'courses':[{'id':'cc','name':'CS','rows':rows}], 'universities':[{'id':str(i),'name':str(i)} for i in range(66)],'foreignCourses':[]}
        fixtures={'data.json':database,'syllabi/records.json':{'foreign':[]},'syllabi/mackenzie-docs.json':{'rows':[{'courseId':'cc','code':'A','name':'Alpha','status':'ementa_oficial_correspondente'}]},'syllabi/comparacoes.json':{'registered':[{'courseId':'cc','phase':'pending'} for _ in range(725)]},'syllabi/revisoes-ementas.json':{'reviews':[{'courseId':'cc'}]*3},'syllabi/pareceres-index.json':{'pareceres':[{'schemaVersion':2,'brazil':{'courseId':'cc'}}]*585},'syllabi/programas.json':{'brazil':{'cc|A':{'officialSyllabus':True},'cc|B':{'officialSyllabus':False}}}}
        class Captured(Exception): pass
        result={}
        def capture(path, value):
            result.update(value)
            raise Captured()
        with patch.object(report_coverage,'read',side_effect=lambda p:fixtures[p]),patch.object(report_coverage,'write',side_effect=capture),self.assertRaises(Captured):
            report_coverage.main()
        metrics=result['metrics']; course=result['mackenzieCourses'][0]
        self.assertEqual(metrics['manualReviews'],585)
        self.assertEqual(metrics['legacyManualReviews'],3)
        self.assertEqual(metrics['mackVerified'],1)
        self.assertEqual(metrics['linkedBrazilianSyllabi'],1)
        self.assertEqual(metrics['withoutBrazilianSyllabus'],1)
        self.assertEqual(course['individualReviews'],585)
        self.assertEqual(course['linkedBrazilianSyllabi'],1)
        self.assertEqual(course['withoutBrazilianSyllabus'],1)
        self.assertEqual([r['code'] for r in course['pendingBrazilianSubjects']],['B'])
