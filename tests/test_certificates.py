import csv,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT))
from guardband.pairings import exact_modular,proof_pairs,validate_modular,theorem1,upper_pairs
from guardband.core import Case,Construction,modular_certificate,validate_lee_interval,clique_check,audit_case
from verify_exports import inspect

class PairingTests(unittest.TestCase):
    def test_all_90_independent_decisions(self):
        feasible=0
        for k in range(1,13):
            for u in range(1,k+2):
                with self.subTest(k=k,u=u):
                    p=exact_modular(k,u)
                    self.assertEqual(p is not None,theorem1(k,u))
                    if p is not None:
                        feasible+=1;validate_modular(p,k,u)
        self.assertEqual(feasible,63)
    def test_table1_literal(self):
        self.assertEqual(modular_certificate(6,3),{1:(12,13),2:(5,7),3:(8,11),4:(6,10),5:(4,9),6:(14,3)})
    def test_general_proof_both_parity_classes(self):
        for k,u in [(1,3),(4,4),(3,1),(7,2),(6,3)]:
            p=proof_pairs(k,u);validate_modular(p,k,u)
            self.assertEqual(sum(b<a for a,b in p.values()),int(k%4 in (2,3)))
    def test_large_certificates(self):
        for k,u in [(30,9),(42,13)]:
            p=modular_certificate(k,u);validate_modular(p,k,u)
            self.assertEqual(p[2*u],(2*k+u-1,u))
    def test_corrupt_pair_rejected(self):
        p=modular_certificate(6,3);p[6]=(14,4)
        with self.assertRaises(ValueError):validate_modular(p,6,3)
    def test_obstruction_only_fixed_phase(self):
        self.assertIsNone(exact_modular(6,4))
        with self.assertRaises(ValueError):proof_pairs(6,4)
    def test_upper_pairs(self):
        for k,u in [(6,3),(12,2)]:
            p=upper_pairs(k,u);flat=[x for ab in p.values() for x in ab]
            self.assertEqual(len(set(flat)),2*k)
            self.assertTrue(all(u<=x<=2*k+u for x in flat))
            self.assertTrue(all(b-a==h for h,(a,b) in p.items()))

class GraphTests(unittest.TestCase):
    def test_lee_interval_and_clique(self):
        for d in range(1,11):
            self.assertTrue(validate_lee_interval(d));self.assertTrue(clique_check(d,2*d+1)['valid'])
    def test_all_fixture_phase_identities(self):
        for row in json.loads((ROOT/'data/fixtures/positive_cases.json').read_text())['cases']:
            c=Construction(Case.from_dict(row))
            self.assertNotEqual(c.opposite_offset_ok(),False)
    def test_invalid_period_closure(self):
        with self.assertRaisesRegex(ValueError,'Period closure'):
            Construction(Case('seam','saturated',2,15,6,2,15,t=2))
    def test_too_short_period(self):
        with self.assertRaises(ValueError):Construction(Case('short','saturated',2,15,4,2,15,t=2))
    def test_palette_mismatch(self):
        with self.assertRaisesRegex(ValueError,'Palette mismatch'):
            Construction(Case('wrong','saturated',2,15,5,2,14,t=2))
    def test_csv_verifier_rejects_corruption(self):
        c=Case('small','saturated',2,15,5,2,15,t=2)
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);self.assertEqual(audit_case(c,folder)['status'],'PASS')
            self.assertEqual(inspect(c.as_dict(),folder)['status'],'PASS')
            p=folder/'edges.csv'
            with p.open(newline='') as f: rows=list(csv.DictReader(f))
            rows[0]['edge_color_from_vertex2']=str(int(rows[0]['edge_color_from_vertex1'])+1)
            with p.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
            self.assertEqual(inspect(c.as_dict(),folder)['status'],'FAIL')

if __name__=='__main__':unittest.main()
