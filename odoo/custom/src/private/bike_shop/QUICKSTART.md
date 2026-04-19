# Bike Shop Module - Quick Start Guide

## Installation

1. **Module Location**: `/odoo/custom/src/private/bike_shop/`
2. **Installation Command**: In Odoo admin, navigate to Apps → Search "Bike Shop" → Install
3. **After Installation**: 
   - Sequence for order numbering is created automatically
   - Menu "Bike Shop" appears in the main menu
   - All security rules are applied

## Menu Navigation

After installation, you'll see in the main menu:

```
Bike Shop
├── Products          → Manage bike shop products
├── Services          → Manage services/labor
├── Customers         → Manage customers (standard Odoo partners)
├── Service Orders    → Create and manage service orders
└── Financial Closings → Generate sales reports by period
```

## Step-by-Step: Creating Your First Order

### Step 1: Create Products
1. Go to **Bike Shop → Products**
2. Click **Create**
3. Fill in:
   - **Product Name**: e.g., "Mountain Bike Wheel"
   - **Product Code**: e.g., "PROD-001" (must be unique)
   - **Selling Price**: e.g., 150.00
   - **Cost Price**: e.g., 80.00
   - **Stock Quantity**: e.g., 10
   - **Color** (optional): e.g., "Black"
4. Click **Save**

### Step 2: Create Services
1. Go to **Bike Shop → Services**
2. Click **Create**
3. Fill in:
   - **Service Name**: e.g., "Wheel Truing"
   - **Service Price**: e.g., 25.00
   - **Description** (optional): e.g., "Wheel alignment and balancing"
4. Click **Save**

### Step 3: Add Customers (if new)
1. Go to **Bike Shop → Customers**
2. Click **Create** (or use existing)
3. Fill in customer details
4. Save

### Step 4: Create Service Order
1. Go to **Bike Shop → Service Orders**
2. Click **Create**
3. **Select Customer**: Choose from dropdown (auto-loads address)
4. **Add Order Lines**:
   - Click **Add a line**
   - Select **Item Type**: Product or Service
   - Select the **Product or Service** (prices auto-populate)
   - Adjust **Quantity** if needed
   - Repeat for multiple items
5. **Apply Discount** (optional):
   - Select discount percentage (0%, 5%, 10%, etc.)
6. **Review**:
   - Subtotal, Discount, and Total auto-calculate
   - Net Value shows profit/loss
7. **Complete Order**:
   - Click **Complete Order** button
   - Stock automatically decreases
   - Status changes to "Completed"

### Step 5: Print Order
1. On the order form, click **Print Order**
2. PDF downloads with all details

### Step 6: Generate Financial Report
1. Go to **Bike Shop → Financial Closings**
2. Click **Create**
3. Enter:
   - **Start Date**: e.g., 2026-04-01
   - **End Date**: e.g., 2026-04-30
4. System automatically:
   - Finds all completed orders in period
   - Calculates sales totals (products + services)
   - Calculates costs and profit
5. Click **Complete Closing** to finalize

---

## Key Features Reference

### Automatic Calculations
- **Subtotal**: Sum of all line items
- **Discount**: Percentage applied to subtotal
- **Total**: Subtotal minus discount
- **Cost Total**: Sum of product costs only
- **Net Value**: Total minus cost total (= profit)

### Inventory Management
- Stock decreases when order completed
- Stock restores if order reopened
- Validation prevents completion if insufficient stock

### Order Statuses
- **Open**: Can edit, not finalized
- **Completed**: Finalized, stock affected, can print

### Discount Options
- 0%, 5%, 10%, 15%, 20%, 25%, 30%

---

## Field Reference

### Products
- Code (unique)
- Name
- Color
- Cost Price & Selling Price
- Stock Quantity
- Barcode (optional, unique)
- NCM (optional)
- Description

### Services
- Name
- Price
- Description

### Orders
- Order Number (auto-generated)
- Customer
- Order Date (auto-filled)
- Status (open/completed)
- Order Items (products and services)
- Discount Percentage
- Calculated Totals

---

## Tips & Tricks

1. **Auto-fill**: When you select a product/service, price and description auto-fill
2. **Bulk Operations**: Edit multiple order lines at once in the tree view
3. **Search Orders**: Use filters to find open, completed, or today's orders
4. **Quick Reports**: View orders grouped by customer or status
5. **Copy Orders**: Duplicate orders as template (when reopened)

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Can't complete order | Check stock availability - validation prevents completion |
| Price not auto-filling | Ensure product/service is marked as "Active" |
| Can't find product | Use search to find by name or code |
| Discount not applying | Select discount percentage from dropdown |
| Stock not decreasing | Order must be "Completed" not just saved |

---

## For Advanced Users

### Extending the Module
- Add custom fields to orders
- Create additional reports
- Implement workflows
- Add email notifications

### Database Queries
- Orders are stored in `bike_shop_order` table
- Products in `bike_shop_product` table
- Services in `bike_shop_service` table
- Order lines in `bike_shop_order_line` table
- Closings in `bike_shop_closing` table

### API Integration
- All models support standard Odoo API
- Can be accessed via XML-RPC or REST endpoints
- Suitable for external system integration

---

## Support

For issues or questions:
1. Check the README.md file for detailed documentation
2. Review IMPLEMENTATION.md for technical details
3. Check the model code for constraints and rules
4. Verify security rules in ir.model.access.csv

---

**Quick Links**
- [README.md](./README.md) - Full documentation
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Technical details
- Models: `models/` directory
- Views: `views/` directory
- Security: `security/ir.model.access.csv`

---

**Happy bike shop management! 🚴**
