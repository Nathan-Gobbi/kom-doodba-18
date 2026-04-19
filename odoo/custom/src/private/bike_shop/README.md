# Bike Shop Module Documentation

## Overview

The Bike Shop module is a comprehensive solution for managing bike shop operations in Odoo 14, built with doodba compatibility. It handles product and service catalog management, service orders with products and labor, inventory control, automated calculations, and financial consolidation reporting.

## Features

### 1. Product Management
- **Product Catalog**: Create and manage bike shop products with:
  - Unique product codes and barcodes
  - Color and NCM (Brazilian product classification) tracking
  - Cost and selling price management
  - Real-time inventory tracking
  - Active/inactive status

### 2. Service Management
- **Service Catalog**: Define labor and service offerings with:
  - Service names and descriptions
  - Service pricing
  - Active/inactive status

### 3. Customer Management
- **Uses Native res.partner**: Leverages Odoo's native partner model for customer management
- **Denormalized Data Storage**: Customer data is copied to orders for historical preservation

### 4. Service Orders (Main Feature)
- **Order Creation**: Create service orders with sequential numbering (BSO/YYYY/00001)
- **Line Items**: Support both products and services in the same order
  - Automatic price and description population
  - Quantity and cost tracking
  - Subtotal calculation

- **Discount Application**: Percentage-based discounts (0-30%)
- **Automatic Calculations**:
  - Subtotal sum
  - Discount amount
  - Final total
  - Cost total
  - Net value (profit)

- **Order Status Management**:
  - Open: Orders in progress
  - Completed: Finalized orders with stock reduction

- **Inventory Control**:
  - Automatic stock decrease when order completes
  - Automatic stock restoration when order reopens
  - Stock availability validation before completion

### 5. Financial Closing/Consolidation
- **Period-based Reporting**: Define periods and get consolidated data
- **Metrics Calculated**:
  - Number of orders
  - Total product sales
  - Total service sales
  - Total sales (products + services - discounts)
  - Product cost totals
  - Net value (profit/loss)
- **Order Reference**: View all orders included in each closing

### 6. Reporting
- **Service Order PDF**: Professional PDF reports for service orders including:
  - Order number and date
  - Customer information and address
  - Complete order items with pricing
  - Total calculations
  - Status and notes

## Data Model

### Models

1. **bike_shop.product**
   - Product catalog with inventory

2. **bike_shop.service**
   - Service definitions

3. **bike_shop.order**
   - Main service order document
   - Aggregates product and service lines
   - Manages pricing and inventory

4. **bike_shop.order.line**
   - Individual items in service orders
   - Supports both products and services

5. **bike_shop.closing**
   - Financial consolidation records
   - Period-based reporting

## Security

- **Group-based Access**: Differentiated permissions for users and administrators
- **Read Permissions**: Users can read products, services, and orders
- **Write Permissions**: Limited write access for regular users
- **Admin Rights**: System administrators have full access

## Menu Structure

```
Bike Shop
├── Products
├── Services
├── Customers
├── Service Orders
└── Financial Closings
```

## Validations

### Product
- Code must be unique
- Barcode must be unique (when provided) and valid format
- Stock cannot be negative
- Prices cannot be negative

### Service
- Price cannot be negative

### Order Line
- Quantity must be greater than zero
- Unit price and cost price cannot be negative
- Product or service must be selected based on line type

### Order
- Stock availability validated before completion

### Closing
- End date must be after start date

## Usage Workflow

### Basic Order Creation
1. Create new Service Order
2. Select customer (auto-loads customer data)
3. Add order lines:
   - Select type (Product or Service)
   - Choose product/service
   - Auto-populated: price, cost, description
   - Adjust quantity as needed
4. Apply discount if needed
5. Review calculated totals
6. Complete order (decreases stock)

### Financial Reporting
1. Create new Financial Closing
2. Enter period dates
3. System automatically finds completed orders in period
4. Review consolidated metrics
5. Mark as completed for record

### PDF Export
- Print button on order form generates professional PDF

## Extension Points

- Custom order line types can be added
- Additional fields can be added to orders and closings
- Custom reports can be created
- Workflow automation can be implemented

## Technical Details

- **Framework**: Odoo 14
- **Dependencies**: base, sale, stock
- **Database Access**: CSV-based security rules
- **Reports**: QWeb template-based PDF generation
- **Sequences**: Automatic order numbering

## Compatibility

- Odoo 14.0+
- Doodba environment
- Multi-currency aware
- Multi-company ready (foundation)

---

For support and updates, please refer to the project repository.
