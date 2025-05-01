# Piat Manager – Order and Inventory Management for Gemstone Trading

## Project Overview

This project is an internal management tool for **Piat**, a company operating in the **gemstone trading and cutting business**, with operations in both Thailand and France.

Piat receives client orders for high-quality, cut gemstones. In response, it places supplier orders for raw or semi-processed stones. These raw stones often do not meet the exact standards required (in terms of size, clarity, or color), requiring **sorting and recutting** before being matched to client specifications.

The business process introduces significant complexity in terms of stock tracking, cost control, and compliance. This system aims to help monitor and optimize these workflows.

## Business Process Summary

1. **Client Order**
   - A client requests specific gemstones (e.g., type, size, shape, quality).
   - Piat commits to delivering stones that meet those specifications.

2. **Supplier Order**
   - Piat purchases stones from suppliers in Thailand.
   - Stones arrive in batches, often with variability in quality and dimensions.

3. **Sorting and Recutting**
   - Stones are sorted:
     - Some meet client requirements immediately.
     - Some are recut to meet client demands.
     - Some are rejected (due to flaws, wrong size, etc.).
   - Rejected or excess stones are added to Piat's general stock.

4. **Client Fulfillment**
   - Suitable stones are sent to the client.
   - Clients inspect the stones and may **return** those that don’t meet expectations.
   - Returned stones re-enter the stock for future use or resale.

5. **Invoicing and Payment**
   - Once accepted, an invoice is issued.
   - Payments can be delayed by several months.
   - Transactions involve **currency fluctuations** (USD ↔ THB).

## Operational Challenges

### 1. Lack of End-to-End Traceability
- There is **no strict link between a specific supplier stone and a specific client delivery**.
- Stones are pooled, sorted, modified, and recombined.
- This creates a **gray area** in stock traceability and cost attribution.

### 2. Stock Accumulation and Losses
- Returned stones and unusable supplier stones increase inventory over time.
- Unsold stock represents **financial losses** (dead stock, sunk costs).

### 3. Timing and Financial Exposure
- Delays between procurement and client payment (sometimes months) introduce:
  - **Currency exchange risks** (USD client → THB supplier).
  - **Uncertainty in tax reporting** (Thailand considers exports as sales, even if returned).

### 4. Compliance and Reporting Complexity
- It's difficult to explain mismatches between imported and sold quantities to tax authorities.
- The system needs to **distinguish between exported, returned, unsold, and sold stones**.

## Goals of This System

- Provide a robust interface for managing **supplier and client orders**.
- Support data correction and cleanup.
- Build a framework to **introduce batch-level stock tracking**, even without full traceability.
- Enable **inventory auditing**, including stone status (sold, returned, in stock, unusable).
- Prepare the ground for **future cost estimation, loss tracking, and fiscal reporting**.

## Next Steps (Planned)

- Introduce a `StoneBatch` model linked to `SupplierOrder`, with:
  - Quantity, weight, and quality information.
  - Status: usable, returned, rejected, in stock, sold.
- Record estimated usage of stock in client orders (even without strict links).
- Implement tools to analyze:
  - Supplier performance.
  - Stone loss rate.
  - Inventory turnover.
  - Return rates.

## Limitations

This system will **not attempt to track individual stones**, as the physical process and historical data do not allow it. Instead, it aims to model reality as precisely as possible **within the limits of available information**.

