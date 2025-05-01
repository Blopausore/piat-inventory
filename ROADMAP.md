# Piat Manager – Roadmap

This roadmap outlines the development milestones for Piat Manager, taking into account the standalone **exchange_rate** application.

## Phase 1 – Data Cleaning and Process Stabilization (In Progress)

**Objectives**

- Finalize the interface for correcting and validating supplier order data
- Support import/export workflows to Excel
- Maintain a robust API and table-based UI outside Django Admin

**Tasks**

- [X] Editable supplier order table (DataTables + AJAX)
- [X] JSON API for listing supplier orders (filters, search, pagination)
- [X] AJAX cell-editing API
- [X] Excel import/export with validation
- [X] Import page and workflow

- [-] Server-side validations (unique constraints, date formats)

## Phase 2 – Integration of exchange_rate App

**Objectives**

- Leverage the existing standalone exchange_rate application to backfill and maintain USD↔THB rates

**Tasks**

- [X] Declare dependency on exchange_rate in Django settings and requirements
- [X] Expose exchange_rate functionality via a service layer: lookup rate by date, from USD to THB (and inverse)
- [ ] On supplier-order import/update, fetch missing rates automatically and allow manual override in the table UI
- [ ] Management command (e.g. backfill_exchange_rates) to populate missing rates on existing records

- Phase 3 – Basic Stock Representation

**Objectives**

- Model batches of gemstones and track their status

**Tasks**

- [ ] Create `StoneBatch` model linked to `SupplierOrder`
- [ ] Add batch attributes: quantity, weight, status, notes
- [ ] Define status options: usable, rejected, in stock, sent to client, returned
- [ ] Build DataTable UI for batch updates
- [ ] Implement batch-level Excel export

## Phase 4 – Link to Client Orders and Estimate Usage

**Objectives**

- Approximate consumption of stock in client orders without strict per-stone traceability

**Tasks**

- [ ] Establish a Many-to-Many relationship between `StoneBatch` and `ClientOrder` with estimated quantities
- [ ] Provide UI controls to assign batches to client orders
- [ ] Display remaining quantities for each batch

## Phase 5 – Loss and Return Analysis

**Objectives**

- Quantify returns and rejections for reporting and business insight

**Tasks**

- [ ] Model return events and update batch status accordingly
- [ ] Allow marking items as “returned to stock,” “unusable,” or “sold”
- [ ] Implement an audit log for all status changes
- [ ] Build summary reports: return rate, loss rate, reuse rate

## Phase 6 – Financial and Compliance Tools

**Objectives**

- Analyze margin impacts and support tax reporting

**Tasks**

- [ ] Compute expected versus actual margins, accounting for payment delays and returns
- [ ] Flag exported stones versus actually sold
- [ ] Generate compliance-ready reports for internal use and tax authorities

## Phase 7 – Optional Enhancements

**Possible Features**

- [ ] User roles and permissions (admin/editor/viewer)
- [ ] Full activity trail and change history
- [ ] Integration with external accounting systems
- [ ] Demand forecasting based on historical usage
