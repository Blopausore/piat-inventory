from django.test import TestCase
from core.order_raw.models import SupplierOrderRaw
from core.supplier_order.services.transform import SupplierOrderTransformer
from core.supplier_order.models import SupplierOrder

class TransformErrorAndDuplicateTests(TestCase):
    def setUp(self):
        # un raw valide minimal pour pouvoir échouer sur date ou carats
        self._counter = 0
        base = {
            'Client Memo': 'P',
            'No.': '1',
            'Date': '2025-05-06',
            'Client': 'TEST#!#!',
            'Stone': 'Ruby',
            'PC': '2',
            'Carats': '1.00',
        }
        self.valid_payload = base.copy()

    def make_raw(self, overrides):
        data = {**self.valid_payload, **overrides}
        idx = self._counter
        self._counter +=1
        return SupplierOrderRaw.objects.create(
            source_file='f.xlsx', sheet_name='S1', row_index=idx, data=data
        )

    def test_should_fail_on_invalid_date_in_transform(self):
        raw = self.make_raw({'Date': '06/05/2025'})
        stats = SupplierOrderTransformer(dry_run=True).run(
            queryset=SupplierOrderRaw.objects.filter(id=raw.id)
        )
        self.assertEqual(stats['orders_created'], 1)
        self.assertEqual(stats['raws_failed'], 0)
        # message d'erreur date présent
        raw = self.make_raw({'Date': '13/13/2000'})
        stats = SupplierOrderTransformer(dry_run=True).run(
            queryset=SupplierOrderRaw.objects.filter(id=raw.id)
        )
        self.assertEqual(stats['orders_created'], 0)
        self.assertGreater(stats['raws_failed'], 0)
        
    def test_should_fail_on_invalid_carats_in_transform(self):
        raw = self.make_raw({'Carats': 'abc'})
        stats = SupplierOrderTransformer(dry_run=True).run(
            queryset=SupplierOrderRaw.objects.filter(id=raw.id)
        )
        self.assertEqual(stats['orders_created'], 0)
        self.assertGreater(stats['raws_failed'], 0)
        err_keys = list(stats['errors'].keys())
        self.assertTrue(any("Decimal" in k or "carats" in k for k in err_keys))

    def test_partially_invalid_row_still_rejected(self):
        # même si les autres champs sont ok, carats invalide => rejet
        raw = self.make_raw({'Carats': 'not-a-number'})
        stats = SupplierOrderTransformer(dry_run=True).run(
            queryset=SupplierOrderRaw.objects.filter(id=raw.id)
        )
        self.assertEqual(stats['orders_created'], 0)
        self.assertEqual(stats['raws_failed'], 1)

    def test_duplicate_skipped_by_bulk_and_clean(self):
        # créer deux raws identiques
        raw1 = self.make_raw({'No.': '10', 'DATE': '2025-05-06'})
        raw2 = self.make_raw({'No.': '10', 'DATE': '2025-05-06'})
        raw1.data["row_index"] = 66
        raw2.data["row_index"] = 67
        # 1er passage crée un order
        t = SupplierOrderTransformer(dry_run=False)
        stats1 = t.run(queryset=SupplierOrderRaw.objects.filter(id=raw1.id))
        self.assertEqual(stats1['orders_created'], 1)
        # 2e passage, même données => bulk_create ignore & clean() rejette
        stats2 = t.run(queryset=SupplierOrderRaw.objects.filter(id=raw2.id))
        self.assertEqual(stats2['raws_failed'], 1)
        self.assertEqual(stats2['orders_created'], 0)
