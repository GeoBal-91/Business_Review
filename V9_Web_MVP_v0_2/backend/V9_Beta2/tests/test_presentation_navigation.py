"""Presentation-only follow-up: pagination, Appendix, cohort note and guide."""
import tempfile
import unittest
from pathlib import Path
from test_regression import run, fixture, zero
from test_hardening import text_of, diagnostic_deck
from test_presentation_patch import blank, full_deck
from presentation_hardening_fixtures import recommendation_rich
from presentation_hardening import recommendation_pages, build_recommendations, action_focus, matrix_cohort_note, add_matrix_cohort_note
from presentation_polish import build_matrix, MATRIX_FOOTNOTE
from beta_presentation import build_methodology as build_guide, METHOD_TITLE, ACTION_TITLE
from data_pipeline import G, N
import numpy as np


def titles(prs):
    return [next((s.text for s in slide.shapes if s.has_text_frame and s.text.strip()), '') for slide in prs.slides]


def plotted(a):
    return a.stores[(a.stores['Store Status']=='Active') & (a.stores['Scoring Status']=='Complete')].dropna(subset=[G,'% CVR'])


class RecommendationPagination(unittest.TestCase):
    def test_requested_group_sizes_and_original_order(self):
        for n, expected in [(0,[0]),(1,[1]),(2,[2]),(3,[3]),(4,[4]),(5,[3,2]),(6,[3,3])]:
            actions=[{'rank':i} for i in range(n)]
            pages=recommendation_pages(actions)
            self.assertEqual([len(p) for p in pages],expected)
            self.assertEqual([a for p in pages for a in p],actions)
            self.assertTrue(all(a is b for a,b in zip([a for p in pages for a in p],actions)))

    def test_four_actions_fit_one_slide_with_all_business_fields(self):
        a=recommendation_rich(store_count=4);self.assertEqual(len(a.actions),4)
        prs=blank();build_recommendations(prs,a)
        self.assertEqual(len(prs.slides),1)
        text=text_of(prs);last=-1
        for action in a.actions:
            pos=text.index(action['Store']);self.assertGreater(pos,last);last=pos
            for key in ['Metric','Issue','Action','Intended Effect']:self.assertIn(action[key],text)
        self.assertEqual(action_focus(a,a.actions)['store_count'],4)
        self.assertIn('Action Focus',text)
        self.assertIn('Stores requiring action\n4',text)

    def test_five_and_six_focus_panel_uses_each_displayed_group(self):
        for n,counts in [(5,[3,2]),(6,[3,3])]:
            a=recommendation_rich(store_count=n);prs=blank();build_recommendations(prs,a)
            self.assertEqual(len(prs.slides),2)
            for slide,group,count in zip(prs.slides,recommendation_pages(a.actions),counts):
                text='\n'.join(s.text for s in slide.shapes if s.has_text_frame)
                self.assertIn(f'Stores requiring action\n{count}',text)
                for action in group:self.assertIn(action['Store'],text)


class NavigationAndCohort(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=recommendation_rich(inactive_count=2)
        cls.prs=full_deck(cls.a)

    def test_appendix_after_thank_you_and_every_diagnostic_retained(self):
        names=titles(self.prs)
        closing=names.index('Thank You');divider=names.index('APPENDIX — Store Diagnostics')
        self.assertEqual(divider,closing+1)
        indices=[i for i,title in enumerate(names) if title=='Store Diagnostics']
        self.assertEqual(len(indices),len(self.a.stores))
        self.assertTrue(all(i>divider for i in indices))
        self.assertTrue(all(t=='Store Diagnostics' or t.startswith('Store Overview') for t in names[divider+1:]))
        actual=[self.prs.slides[i]._element.xml for i in indices]
        expected=[s._element.xml for s in diagnostic_deck(self.a).slides]
        self.assertEqual(actual,expected)

    def test_beta_methodology_after_top_gmv_before_actions(self):
        names=titles(self.prs)
        index=names.index(METHOD_TITLE)
        self.assertEqual(index,names.index('Top GMV Stores')+1)
        self.assertEqual(names.count(METHOD_TITLE),1)
        self.assertTrue(names[index+1].startswith(ACTION_TITLE))
        standalone=blank();build_guide(standalone,self.a)
        self.assertEqual(self.prs.slides[index]._element.xml,standalone.slides[0]._element.xml)

    def test_guide_after_fallback_cover_when_market_period_unavailable(self):
        a=run(benchmarks=[fixture(month='June')])
        names=titles(full_deck(a))
        self.assertEqual(names.index(METHOD_TITLE),names.index('Top GMV Stores')+1)

    def test_matrix_note_counts_no_activity_separately(self):
        note=matrix_cohort_note(self.a,plotted(self.a))
        self.assertEqual(note,'6 stores plotted · 2 No Activity stores reviewed separately.')
        matrix=next(s for s in self.prs.slides if any(t.has_text_frame and t.text=='Store Performance Matrix' for t in s.shapes))
        self.assertTrue(any(s.has_text_frame and s.text==note for s in matrix.shapes))
        self.assertTrue(any(s.has_text_frame and s.text==MATRIX_FOOTNOTE for s in matrix.shapes))

    def test_cohort_note_dynamic_counts_and_nonassessed_categories(self):
        rows=[fixture(f'A{i}') for i in range(16)]+[zero('Idle1'),zero('Idle2')]
        a=run(rows)
        self.assertEqual(matrix_cohort_note(a,plotted(a)), '16 stores plotted · 2 No Activity stores reviewed separately.')
        b=run([fixture('Known'),fixture('Gone','July'),zero('Idle'),fixture('Incomplete',**{N:np.nan}),fixture('NoGMV',**{G:np.nan})])
        note=matrix_cohort_note(b,plotted(b))
        for text in ['1 store plotted','4 reviewed separately','1 Unknown','1 No Activity','1 Active / incomplete','1 Active / missing matrix inputs']:
            self.assertIn(text,note)

    def test_cohort_note_repeats_on_each_legend_continuation(self):
        a=run([fixture(str(i),**{'Store Address Address':f'Long address {i}, Avenue of the City, Tbilisi, Georgia'}) for i in range(28)])
        prs=blank()
        with tempfile.TemporaryDirectory() as tmp:build_matrix(prs,a,plotted(a),lambda n:str(Path(tmp)/n))
        self.assertGreater(len(prs.slides),1)
        add_matrix_cohort_note(list(prs.slides),a,plotted(a))
        for slide in prs.slides:
            notes=[s for s in slide.shapes if s.name=='Matrix cohort note']
            self.assertEqual(len(notes),1)
            self.assertEqual(notes[0].text,'28 stores plotted · 0 stores reviewed separately.')

    def test_empty_matrix_cohort_note_preserves_inactive_evidence(self):
        a=run([zero()])
        self.assertEqual(matrix_cohort_note(a,plotted(a)),'0 stores plotted · 1 No Activity store reviewed separately.')
