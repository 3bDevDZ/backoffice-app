from flask import Blueprint, request, send_file, Response
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.products.commands.commands import (
    CreateProductCommand, UpdateProductCommand, ArchiveProductCommand, DeleteProductCommand,
    ActivateProductCommand, DeactivateProductCommand,
    CreateCategoryCommand, UpdateCategoryCommand, DeleteCategoryCommand
)
from app.application.products.queries.queries import (
    GetProductByIdQuery, ListProductsQuery, SearchProductsQuery,
    GetCategoryByIdQuery, ListCategoriesQuery, GetPriceHistoryQuery, GetCostHistoryQuery
)
from app.application.products.variants.commands.commands import (
    CreateVariantCommand, UpdateVariantCommand, ArchiveVariantCommand,
    ActivateVariantCommand, DeleteVariantCommand
)
from app.application.products.variants.queries.queries import (
    GetVariantByIdQuery, GetVariantsByProductQuery, ListVariantsQuery
)
from app.application.products.pricing.commands.commands import (
    CreatePriceListCommand, UpdatePriceListCommand, DeletePriceListCommand,
    AddProductToPriceListCommand, UpdateProductPriceInListCommand, RemoveProductFromPriceListCommand,
    CreateVolumePricingCommand, UpdateVolumePricingCommand, DeleteVolumePricingCommand
)
from app.application.products.pricing.queries.queries import (
    ListPriceListsQuery, GetPriceListByIdQuery, GetProductsInPriceListQuery,
    GetVolumePricingQuery
)
from app.api.schemas.product_schema import (
    ProductCreateSchema, ProductUpdateSchema, ProductSchema,
    CategoryCreateSchema, CategoryUpdateSchema, CategorySchema
)
from app.security.rbac import require_roles
from app.utils.response import success_response, error_response, paginated_response
from app.services.import_export import ImportExportService
from decimal import Decimal
import io

products_bp = Blueprint("products", __name__)

# Product Endpoints
@products_bp.get("")
@require_roles("admin", "commercial", "direction")
def list_products():
    """List products with pagination, search, and filters. Supports locale parameter (?locale=fr|ar)."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        search = request.args.get("search")
        category_id = request.args.get("category_id", type=int)
        status = request.args.get("status")
        
        query = ListProductsQuery(
            page=page,
            per_page=per_page,
            search=search,
            category_id=category_id,
            status=status
        )
        products = mediator.dispatch(query)
        
        # TODO: Get total count for pagination
        total = len(products)  # Simplified - should query total count
        return paginated_response(
            items=[ProductSchema().dump(p) for p in products],
            total=total,
            page=page,
            page_size=per_page
        )
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.get("/<int:product_id>")
@require_roles("admin", "commercial", "direction")
def get_product(product_id: int):
    """Get product by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        product = mediator.dispatch(GetProductByIdQuery(id=product_id))
        return success_response(ProductSchema().dump(product))
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.get("/<int:product_id>/price-history")
@require_roles("admin", "commercial", "direction")
def get_price_history(product_id: int):
    """Get price history for a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        limit = request.args.get("limit", type=int, default=100)
        query = GetPriceHistoryQuery(product_id=product_id, limit=limit)
        history = mediator.dispatch(query)
        
        # Convert DTOs to dict for JSON serialization
        history_data = [
            {
                'id': entry.id,
                'product_id': entry.product_id,
                'old_price': float(entry.old_price) if entry.old_price else None,
                'new_price': float(entry.new_price),
                'changed_by': entry.changed_by,
                'changed_by_username': entry.changed_by_username,
                'changed_at': entry.changed_at.isoformat() if entry.changed_at else None,
                'reason': entry.reason
            }
            for entry in history
        ]
        
        return success_response(history_data)
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.get("/<int:product_id>/cost-history")
@require_roles("admin", "commercial", "direction")
def get_cost_history(product_id: int):
    """Get cost history for a product (AVCO method). Supports locale parameter (?locale=fr|ar)."""
    try:
        limit = request.args.get("limit", type=int, default=100)
        query = GetCostHistoryQuery(product_id=product_id, limit=limit)
        history = mediator.dispatch(query)
        
        # Convert DTOs to dict for JSON serialization
        history_data = [
            {
                'id': entry.id,
                'product_id': entry.product_id,
                'old_cost': float(entry.old_cost) if entry.old_cost else None,
                'new_cost': float(entry.new_cost),
                'old_stock': float(entry.old_stock) if entry.old_stock else None,
                'new_stock': float(entry.new_stock),
                'purchase_price': float(entry.purchase_price),
                'quantity_received': float(entry.quantity_received),
                'changed_by': entry.changed_by,
                'changed_by_username': entry.changed_by_username,
                'changed_at': entry.changed_at.isoformat() if entry.changed_at else None,
                'reason': entry.reason,
                'purchase_order_id': entry.purchase_order_id,
                'purchase_order_line_id': entry.purchase_order_line_id
            }
            for entry in history
        ]
        
        return success_response(history_data)
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("")
@require_roles("admin", "commercial")
def create():
    """Create a new product. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = ProductCreateSchema().load(request.get_json() or {})
        # Remove locale from data if present (not part of product schema)
        data.pop('locale', None)
        command = CreateProductCommand(**data)
        product = mediator.dispatch(command)
        return success_response(ProductSchema().dump(product), message=_('Product created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create product: {}').format(str(e)), status_code=500)


@products_bp.put("/<int:product_id>")
@require_roles("admin", "commercial")
def update(product_id: int):
    """Update a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = ProductUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)  # Remove locale if present
        command = UpdateProductCommand(id=product_id, **data)
        product = mediator.dispatch(command)
        return success_response(ProductSchema().dump(product), message=_('Product updated successfully'))
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.delete("/<int:product_id>")
@require_roles("admin")
def delete(product_id: int):
    """Delete a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeleteProductCommand(id=product_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Product deleted successfully'), status_code=204)
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/<int:product_id>/archive")
@require_roles("admin")
def archive(product_id: int):
    """Archive a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = ArchiveProductCommand(id=product_id)
        product = mediator.dispatch(command)
        return success_response(ProductSchema().dump(product), message=_('Product archived successfully'))
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/<int:product_id>/activate")
@require_roles("admin", "commercial")
def activate(product_id: int):
    """Activate a product (set status to 'active'). Supports locale parameter (?locale=fr|ar)."""
    try:
        command = ActivateProductCommand(id=product_id)
        product = mediator.dispatch(command)
        return success_response(ProductSchema().dump(product), message=_('Product activated successfully'))
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/<int:product_id>/deactivate")
@require_roles("admin", "commercial")
def deactivate(product_id: int):
    """Deactivate a product (set status to 'inactive'). Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeactivateProductCommand(id=product_id)
        product = mediator.dispatch(command)
        return success_response(ProductSchema().dump(product), message=_('Product deactivated successfully'))
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.get("/search")
@require_roles("admin", "commercial", "direction")
def search_products():
    """Search products. Supports locale parameter (?locale=fr|ar)."""
    try:
        search_term = request.args.get("q", "")
        limit = min(int(request.args.get("limit", 20)), 100)
        
        if not search_term:
            return error_response(_('Search term is required'), status_code=400)
        
        query = SearchProductsQuery(search_term=search_term, limit=limit)
        products = mediator.dispatch(query)
        return success_response([ProductSchema().dump(p) for p in products])
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# Category Endpoints
@products_bp.get("/categories")
@require_roles("admin", "commercial", "direction")
def list_categories():
    """List categories. Supports locale parameter (?locale=fr|ar)."""
    try:
        parent_id = request.args.get("parent_id", type=int)
        query = ListCategoriesQuery(parent_id=parent_id)
        categories = mediator.dispatch(query)
        return success_response([CategorySchema().dump(c) for c in categories])
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.get("/categories/<int:category_id>")
@require_roles("admin", "commercial", "direction")
def get_category(category_id: int):
    """Get category by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        category = mediator.dispatch(GetCategoryByIdQuery(id=category_id))
        return success_response(CategorySchema().dump(category))
    except ValueError as e:
        return error_response(_('Category not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/categories")
@require_roles("admin", "commercial")
def create_category():
    """Create a new category. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = CategoryCreateSchema().load(request.get_json() or {})
        data.pop('locale', None)  # Remove locale if present
        command = CreateCategoryCommand(**data)
        category = mediator.dispatch(command)
        return success_response(CategorySchema().dump(category), message=_('Category created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create category: {}').format(str(e)), status_code=500)


@products_bp.put("/categories/<int:category_id>")
@require_roles("admin", "commercial")
def update_category(category_id: int):
    """Update a category. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = CategoryUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)  # Remove locale if present
        command = UpdateCategoryCommand(id=category_id, **data)
        category = mediator.dispatch(command)
        return success_response(CategorySchema().dump(category), message=_('Category updated successfully'))
    except ValueError as e:
        return error_response(_('Category not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.delete("/categories/<int:category_id>")
@require_roles("admin")
def delete_category(category_id: int):
    try:
        command = DeleteCategoryCommand(id=category_id)
        mediator.dispatch(command)
        return success_response(None, status_code=204)
    except ValueError as e:
        return error_response(_(str(e)), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# Import/Export Endpoints
@products_bp.post("/import")
@require_roles("admin", "commercial")
def import_products():
    """Import products from CSV or Excel file."""
    try:
        if 'file' not in request.files:
            return error_response(_('No file provided'), status_code=400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response(_('No file selected'), status_code=400)
        
        # Get format from filename or content type
        filename = file.filename.lower()
        file_content = file.read()
        
        # Get categories for mapping
        categories_query = ListCategoriesQuery()
        categories = mediator.dispatch(categories_query)
        category_map = {cat.name: cat.id for cat in categories}
        
        # Import based on file type
        if filename.endswith('.csv'):
            csv_content = file_content.decode('utf-8')
            result = ImportExportService.import_products_from_csv(csv_content, category_map)
        elif filename.endswith(('.xlsx', '.xls')):
            result = ImportExportService.import_products_from_excel(file_content, category_map)
        else:
            return error_response(_('Unsupported file format. Please use CSV or Excel files.'), status_code=400)
        
        # Create products from successful imports
        created = []
        for product_data in result['success']:
            try:
                command = CreateProductCommand(**product_data)
                product = mediator.dispatch(command)
                created.append(ProductSchema().dump(product))
            except Exception as e:
                result['errors'].append({
                    'code': product_data.get('code', ''),
                    'error': str(e)
                })
        
        return success_response({
            'created': len(created),
            'errors': len(result['errors']),
            'products': created,
            'error_details': result['errors']
        })
        
    except Exception as e:
        return error_response(_('Import failed: {}').format(str(e)), status_code=500)


@products_bp.get("/export")
@require_roles("admin", "commercial", "direction")
def export_products():
    """Export products to CSV or Excel file."""
    try:
        format_type = request.args.get('format', 'csv').lower()  # csv or excel
        
        # Get all products (or filtered)
        search = request.args.get('search')
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')
        
        query = ListProductsQuery(
            page=1,
            per_page=10000,  # Large limit for export
            search=search,
            category_id=category_id,
            status=status
        )
        products = mediator.dispatch(query)
        
        # Convert to dictionaries
        products_data = [ProductSchema().dump(p) for p in products]
        
        if format_type == 'excel':
            excel_bytes = ImportExportService.export_products_to_excel(products_data)
            return send_file(
                io.BytesIO(excel_bytes),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='products_export.xlsx'
            )
        else:  # CSV
            csv_content = ImportExportService.export_products_to_csv(products_data)
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=products_export.csv'}
            )
            
    except Exception as e:
        return error_response(_('Export failed: {}').format(str(e)), status_code=500)


# Product Variant Endpoints
@products_bp.get("/<int:product_id>/variants")
@require_roles("admin", "commercial", "direction")
def list_variants(product_id: int):
    """List all variants for a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        include_archived = request.args.get("include_archived", "false").lower() == "true"
        query = GetVariantsByProductQuery(
            product_id=product_id,
            include_archived=include_archived
        )
        variants = mediator.dispatch(query)
        return success_response([{
            'id': v.id,
            'product_id': v.product_id,
            'product_code': v.product_code,
            'product_name': v.product_name,
            'code': v.code,
            'name': v.name,
            'attributes': v.attributes,
            'price': float(v.price) if v.price else None,
            'cost': float(v.cost) if v.cost else None,
            'barcode': v.barcode,
            'status': v.status,
            'created_at': v.created_at.isoformat() if v.created_at else None
        } for v in variants])
    except ValueError as e:
        return error_response(_(str(e)), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/<int:product_id>/variants")
@require_roles("admin", "commercial")
def create_variant(product_id: int):
    """Create a new variant for a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        data.pop('locale', None)  # Remove locale if present
        command = CreateVariantCommand(
            product_id=product_id,
            code=data.get('code'),
            name=data.get('name'),
            attributes=data.get('attributes'),
            price=Decimal(str(data['price'])) if data.get('price') is not None else None,
            cost=Decimal(str(data['cost'])) if data.get('cost') is not None else None,
            barcode=data.get('barcode')
        )
        variant = mediator.dispatch(command)
        return success_response({
            'id': variant.id,
            'product_id': variant.product_id,
            'code': variant.code,
            'name': variant.name,
            'attributes': variant.attributes,
            'price': float(variant.price) if variant.price else None,
            'cost': float(variant.cost) if variant.cost else None,
            'barcode': variant.barcode,
            'status': variant.status
        }, message=_('Variant created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create variant: {}').format(str(e)), status_code=500)


@products_bp.get("/variants/<int:variant_id>")
@require_roles("admin", "commercial", "direction")
def get_variant(variant_id: int):
    """Get variant by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        query = GetVariantByIdQuery(id=variant_id)
        variant = mediator.dispatch(query)
        return success_response({
            'id': variant.id,
            'product_id': variant.product_id,
            'product_code': variant.product_code,
            'product_name': variant.product_name,
            'code': variant.code,
            'name': variant.name,
            'attributes': variant.attributes,
            'price': float(variant.price) if variant.price else None,
            'cost': float(variant.cost) if variant.cost else None,
            'barcode': variant.barcode,
            'status': variant.status,
            'created_at': variant.created_at.isoformat() if variant.created_at else None
        })
    except ValueError as e:
        return error_response(_('Variant not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.put("/variants/<int:variant_id>")
@require_roles("admin", "commercial")
def update_variant(variant_id: int):
    """Update a variant. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        data.pop('locale', None)  # Remove locale if present
        command = UpdateVariantCommand(
            id=variant_id,
            name=data.get('name'),
            attributes=data.get('attributes'),
            price=Decimal(str(data['price'])) if data.get('price') is not None else None,
            cost=Decimal(str(data['cost'])) if data.get('cost') is not None else None,
            barcode=data.get('barcode')
        )
        variant = mediator.dispatch(command)
        return success_response({
            'id': variant.id,
            'product_id': variant.product_id,
            'code': variant.code,
            'name': variant.name,
            'attributes': variant.attributes,
            'price': float(variant.price) if variant.price else None,
            'cost': float(variant.cost) if variant.cost else None,
            'barcode': variant.barcode,
            'status': variant.status
        }, message=_('Variant updated successfully'))
    except ValueError as e:
        return error_response(_('Variant not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.delete("/variants/<int:variant_id>")
@require_roles("admin", "commercial")
def delete_variant(variant_id: int):
    """Delete a variant. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeleteVariantCommand(id=variant_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Variant deleted successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to delete variant: {}').format(str(e)), status_code=500)


@products_bp.post("/variants/<int:variant_id>/archive")
@require_roles("admin", "commercial")
def archive_variant(variant_id: int):
    """Archive a variant. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = ArchiveVariantCommand(id=variant_id)
        variant = mediator.dispatch(command)
        return success_response({
            'id': variant.id,
            'status': variant.status
        }, message=_('Variant archived successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to archive variant: {}').format(str(e)), status_code=500)


@products_bp.post("/variants/<int:variant_id>/activate")
@require_roles("admin", "commercial")
def activate_variant(variant_id: int):
    """Activate an archived variant. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = ActivateVariantCommand(id=variant_id)
        variant = mediator.dispatch(command)
        return success_response({
            'id': variant.id,
            'status': variant.status
        }, message=_('Variant activated successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to activate variant: {}').format(str(e)), status_code=500)


# ==================== Price List Endpoints ====================

@products_bp.get("/price-lists")
@require_roles("admin", "commercial", "direction")
def list_price_lists():
    """List price lists with pagination and filtering. Supports locale parameter (?locale=fr|ar)."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        search = request.args.get("search")
        is_active = request.args.get("is_active")
        if is_active is not None:
            is_active = is_active.lower() == 'true'
        
        query = ListPriceListsQuery(
            page=page,
            per_page=per_page,
            search=search,
            is_active=is_active
        )
        result = mediator.dispatch(query)
        
        # Convert DTOs to dict
        items = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'is_active': item.is_active,
                'product_count': item.product_count,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None
            }
            for item in result['items']
        ]
        
        return paginated_response(items, result['total'], result['page'], result['per_page'])
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/price-lists")
@require_roles("admin", "commercial")
def create_price_list():
    """Create a new price list. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json()
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        command = CreatePriceListCommand(
            name=data.get('name'),
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        price_list = mediator.dispatch(command)
        
        return success_response({
            'id': price_list.id,
            'name': price_list.name,
            'description': price_list.description,
            'is_active': price_list.is_active
        }, message=_('Price list created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.get("/price-lists/<int:price_list_id>")
@require_roles("admin", "commercial", "direction")
def get_price_list(price_list_id: int):
    """Get a price list by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        query = GetPriceListByIdQuery(id=price_list_id)
        price_list = mediator.dispatch(query)
        
        return success_response({
            'id': price_list.id,
            'name': price_list.name,
            'description': price_list.description,
            'is_active': price_list.is_active,
            'product_count': price_list.product_count,
            'created_at': price_list.created_at.isoformat() if price_list.created_at else None,
            'updated_at': price_list.updated_at.isoformat() if price_list.updated_at else None
        })
    except ValueError as e:
        return error_response(_('Price list not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.put("/price-lists/<int:price_list_id>")
@require_roles("admin", "commercial")
def update_price_list(price_list_id: int):
    """Update a price list. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json()
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        command = UpdatePriceListCommand(
            id=price_list_id,
            name=data.get('name'),
            description=data.get('description'),
            is_active=data.get('is_active')
        )
        price_list = mediator.dispatch(command)
        
        return success_response({
            'id': price_list.id,
            'name': price_list.name,
            'description': price_list.description,
            'is_active': price_list.is_active
        }, message=_('Price list updated successfully'))
    except ValueError as e:
        return error_response(_('Price list not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.delete("/price-lists/<int:price_list_id>")
@require_roles("admin", "commercial")
def delete_price_list(price_list_id: int):
    """Delete a price list. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeletePriceListCommand(id=price_list_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Price list deleted successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# ==================== Volume Pricing Endpoints ====================

@products_bp.get("/products/<int:product_id>/volume-pricing")
@require_roles("admin", "commercial", "direction")
def get_volume_pricing(product_id: int):
    """Get all volume pricing tiers for a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        query = GetVolumePricingQuery(product_id=product_id)
        tiers = mediator.dispatch(query)
        
        # Convert DTOs to dict
        items = [
            {
                'id': tier.id,
                'product_id': tier.product_id,
                'min_quantity': float(tier.min_quantity),
                'max_quantity': float(tier.max_quantity) if tier.max_quantity else None,
                'price': float(tier.price),
                'created_at': tier.created_at.isoformat() if tier.created_at else None,
                'updated_at': tier.updated_at.isoformat() if tier.updated_at else None
            }
            for tier in tiers
        ]
        
        return success_response({'items': items})
    except ValueError as e:
        return error_response(_('Product not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/products/<int:product_id>/volume-pricing")
@require_roles("admin", "commercial")
def create_volume_pricing(product_id: int):
    """Create a volume pricing tier for a product. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json()
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        min_quantity = Decimal(str(data.get('min_quantity')))
        max_quantity = Decimal(str(data.get('max_quantity'))) if data.get('max_quantity') else None
        price = Decimal(str(data.get('price')))
        
        command = CreateVolumePricingCommand(
            product_id=product_id,
            min_quantity=min_quantity,
            max_quantity=max_quantity,
            price=price
        )
        tier = mediator.dispatch(command)
        
        return success_response({
            'id': tier.id,
            'product_id': tier.product_id,
            'min_quantity': float(tier.min_quantity),
            'max_quantity': float(tier.max_quantity) if tier.max_quantity else None,
            'price': float(tier.price),
            'created_at': tier.created_at.isoformat() if tier.created_at else None,
            'updated_at': tier.updated_at.isoformat() if tier.updated_at else None
        }, status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.put("/volume-pricing/<int:tier_id>")
@require_roles("admin", "commercial")
def update_volume_pricing(tier_id: int):
    """Update a volume pricing tier. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json()
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        min_quantity = Decimal(str(data.get('min_quantity'))) if data.get('min_quantity') is not None else None
        max_quantity = Decimal(str(data.get('max_quantity'))) if data.get('max_quantity') is not None else None
        price = Decimal(str(data.get('price'))) if data.get('price') is not None else None
        
        command = UpdateVolumePricingCommand(
            id=tier_id,
            min_quantity=min_quantity,
            max_quantity=max_quantity,
            price=price
        )
        tier = mediator.dispatch(command)
        
        return success_response({
            'id': tier.id,
            'product_id': tier.product_id,
            'min_quantity': float(tier.min_quantity),
            'max_quantity': float(tier.max_quantity) if tier.max_quantity else None,
            'price': float(tier.price),
            'created_at': tier.created_at.isoformat() if tier.created_at else None,
            'updated_at': tier.updated_at.isoformat() if tier.updated_at else None
        })
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.delete("/volume-pricing/<int:tier_id>")
@require_roles("admin", "commercial")
def delete_volume_pricing(tier_id: int):
    """Delete a volume pricing tier. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeleteVolumePricingCommand(id=tier_id)
        mediator.dispatch(command)
        
        return success_response({'message': _('Volume pricing tier deleted successfully')})
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# ==================== Product Price List Endpoints ====================

@products_bp.get("/price-lists/<int:price_list_id>/products")
@require_roles("admin", "commercial", "direction")
def get_products_in_price_list(price_list_id: int):
    """Get all products in a price list. Supports locale parameter (?locale=fr|ar)."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        search = request.args.get("search")
        
        query = GetProductsInPriceListQuery(
            price_list_id=price_list_id,
            page=page,
            per_page=per_page,
            search=search
        )
        result = mediator.dispatch(query)
        
        # Convert DTOs to dict
        items = [
            {
                'id': item.id,
                'price_list_id': item.price_list_id,
                'price_list_name': item.price_list_name,
                'product_id': item.product_id,
                'product_code': item.product_code,
                'product_name': item.product_name,
                'price': float(item.price),
                'base_price': float(item.base_price),
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None
            }
            for item in result['items']
        ]
        
        return paginated_response(items, result['total'], result['page'], result['per_page'])
    except ValueError as e:
        return error_response(_('Price list not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.post("/price-lists/<int:price_list_id>/products")
@require_roles("admin", "commercial")
def add_product_to_price_list(price_list_id: int):
    """Add a product to a price list. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json()
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        product_id = data.get('product_id')
        price = data.get('price')
        
        if not product_id:
            return error_response(_('product_id is required'), status_code=400)
        if price is None:
            return error_response(_('price is required'), status_code=400)
        
        command = AddProductToPriceListCommand(
            price_list_id=price_list_id,
            product_id=product_id,
            price=Decimal(str(price))
        )
        product_price_list = mediator.dispatch(command)
        
        return success_response({
            'id': product_price_list.id,
            'price_list_id': product_price_list.price_list_id,
            'product_id': product_price_list.product_id,
            'price': float(product_price_list.price)
        }, message=_('Product added to price list successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.put("/price-lists/<int:price_list_id>/products/<int:product_id>")
@require_roles("admin", "commercial")
def update_product_price_in_list(price_list_id: int, product_id: int):
    """Update a product's price in a price list. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json()
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        price = data.get('price')
        if price is None:
            return error_response(_('price is required'), status_code=400)
        
        command = UpdateProductPriceInListCommand(
            price_list_id=price_list_id,
            product_id=product_id,
            price=Decimal(str(price))
        )
        product_price_list = mediator.dispatch(command)
        
        return success_response({
            'id': product_price_list.id,
            'price_list_id': product_price_list.price_list_id,
            'product_id': product_price_list.product_id,
            'price': float(product_price_list.price)
        }, message=_('Product price updated successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@products_bp.delete("/price-lists/<int:price_list_id>/products/<int:product_id>")
@require_roles("admin", "commercial")
def remove_product_from_price_list(price_list_id: int, product_id: int):
    """Remove a product from a price list. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = RemoveProductFromPriceListCommand(
            price_list_id=price_list_id,
            product_id=product_id
        )
        mediator.dispatch(command)
        return success_response(None, message=_('Product removed from price list successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)