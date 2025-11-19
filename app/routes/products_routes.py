"""Frontend route handlers for product management pages."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import get_locale, gettext as _
from decimal import Decimal
import re
from app.application.common.mediator import mediator
from app.application.products.queries.queries import ListProductsQuery, GetProductByIdQuery, ListCategoriesQuery, GetPriceHistoryQuery, GetCostHistoryQuery
from app.application.products.pricing.queries.queries import (
    ListPriceListsQuery, GetPriceListByIdQuery, GetProductsInPriceListQuery, GetVolumePricingQuery,
    GetActivePromotionalPricesQuery, GetPromotionalPricesByProductQuery
)
from app.application.products.pricing.commands.commands import (
    CreatePriceListCommand, UpdatePriceListCommand, DeletePriceListCommand,
    AddProductToPriceListCommand, UpdateProductPriceInListCommand, RemoveProductFromPriceListCommand,
    CreateVolumePricingCommand, UpdateVolumePricingCommand, DeleteVolumePricingCommand,
    CreatePromotionalPriceCommand, UpdatePromotionalPriceCommand, DeletePromotionalPriceCommand
)
from app.application.products.commands.commands import (
    CreateProductCommand, UpdateProductCommand, ArchiveProductCommand,
    DeleteProductCommand, ActivateProductCommand, DeactivateProductCommand
)
from app.application.products.variants.queries.queries import GetVariantsByProductQuery, GetVariantByIdQuery
from app.application.products.variants.commands.commands import (
    CreateVariantCommand, UpdateVariantCommand, ArchiveVariantCommand,
    ActivateVariantCommand, DeleteVariantCommand
)
from app.security.session_auth import require_roles_or_redirect, get_current_user

products_routes = Blueprint('products_frontend', __name__)


@products_routes.route('/products')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list():
    """Render products list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    
    # Fetch products via query
    query = ListProductsQuery(
        page=page,
        per_page=per_page,
        search=search,
        category_id=category_id,
        status=status
    )
    products = mediator.dispatch(query)
    
    # Fetch categories for filter dropdown
    categories_query = ListCategoriesQuery()
    categories = mediator.dispatch(categories_query)
    
    return render_template(
        'products/list.html',
        products=products,
        categories=categories,
        page=page,
        per_page=per_page,
        search=search,
        category_id=category_id,
        status=status,
        locale=locale,
        direction=direction
    )


@products_routes.route('/products/new')
@require_roles_or_redirect('admin', 'commercial')
def new():
    """Render new product form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch categories for form
    categories_query = ListCategoriesQuery()
    categories = mediator.dispatch(categories_query)
    
    return render_template(
        'products/form.html',
        product=None,
        categories=categories,
        locale=locale,
        direction=direction
    )


@products_routes.route('/products/<int:product_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit(product_id: int):
    """Render edit product form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch product
    product = mediator.dispatch(GetProductByIdQuery(id=product_id))
    
    # Fetch categories for form
    categories_query = ListCategoriesQuery()
    categories = mediator.dispatch(categories_query)
    
    return render_template(
        'products/form.html',
        product=product,
        categories=categories,
        locale=locale,
        direction=direction
    )


@products_routes.route('/products', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def create():
    """Handle product creation form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract product data
        from decimal import Decimal
        product_data = {
            'name': data.get('name'),
            'code': data.get('code'),
            'barcode': data.get('barcode') or None,
            'description': data.get('description') or None,
            'price': Decimal(str(data.get('price', 0))) if data.get('price') else Decimal('0'),
            'cost': Decimal(str(data.get('cost'))) if data.get('cost') else None,
            'unit_of_measure': data.get('unit') or 'piece',
            'category_ids': [int(cid) for cid in data.get('category_ids', [])] if isinstance(data.get('category_ids'), list) else []
        }
        
        # Create product
        command = CreateProductCommand(**product_data)
        product = mediator.dispatch(command)
        
        flash(_('Product created successfully'), 'success')
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': _('Product created successfully'),
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'code': product.code,
                    'cost': float(product.cost) if product.cost else None,
                    'price': float(product.price) if product.price else None
                }
            }), 201
        else:
            return redirect(url_for('products_frontend.list'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.new'))
    except Exception as e:
        error_msg = _('Failed to create product: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.new'))


@products_routes.route('/products/<int:product_id>', methods=['PUT', 'POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_product(product_id: int):
    """Handle product update form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract product data
        from decimal import Decimal
        update_data = {}
        if 'name' in data:
            update_data['name'] = data.get('name')
        if 'code' in data:
            update_data['code'] = data.get('code')
        if 'barcode' in data:
            update_data['barcode'] = data.get('barcode') or None
        if 'description' in data:
            update_data['description'] = data.get('description') or None
        if 'cost' in data:
            update_data['cost'] = Decimal(str(data.get('cost'))) if data.get('cost') else None
        if 'price' in data:
            update_data['price'] = Decimal(str(data.get('price'))) if data.get('price') else None
        if 'unit' in data:
            update_data['unit_of_measure'] = data.get('unit')
        if 'category_ids' in data:
            update_data['category_ids'] = [int(cid) for cid in data.get('category_ids', [])] if isinstance(data.get('category_ids'), list) else []
        
        # Update product
        command = UpdateProductCommand(id=product_id, **update_data)
        mediator.dispatch(command)
        
        flash(_('Product updated successfully'), 'success')
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': _('Product updated successfully')
            })
        else:
            return redirect(url_for('products_frontend.list'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.edit', product_id=product_id))
    except Exception as e:
        error_msg = _('Failed to update product: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.edit', product_id=product_id))


@products_routes.route('/products/<int:product_id>/activate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def activate_product(product_id: int):
    """Activate a product."""
    try:
        command = ActivateProductCommand(id=product_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Product activated successfully')})
        flash(_('Product activated successfully'), 'success')
        return redirect(url_for('products_frontend.list'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.list'))


@products_routes.route('/products/<int:product_id>/deactivate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def deactivate_product(product_id: int):
    """Deactivate a product."""
    try:
        command = DeactivateProductCommand(id=product_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Product deactivated successfully')})
        flash(_('Product deactivated successfully'), 'success')
        return redirect(url_for('products_frontend.list'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.list'))


@products_routes.route('/products/<int:product_id>/archive', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def archive_product(product_id: int):
    """Archive a product."""
    try:
        command = ArchiveProductCommand(id=product_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Product archived successfully')})
        flash(_('Product archived successfully'), 'success')
        return redirect(url_for('products_frontend.list'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.list'))


@products_routes.route('/products/<int:product_id>', methods=['DELETE'])
@require_roles_or_redirect('admin', 'commercial')
def delete_product(product_id: int):
    """Delete a product."""
    try:
        command = DeleteProductCommand(id=product_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Product deleted successfully')})
        flash(_('Product deleted successfully'), 'success')
        return redirect(url_for('products_frontend.list'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('products_frontend.list'))


@products_routes.route('/products/export')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def export():
    """Handle product export request - redirects to API endpoint."""
    # Build API URL with query parameters
    search = request.args.get('search')
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    format_type = request.args.get('format', 'csv')
    
    # Build query string
    query_parts = [f'format={format_type}']
    if search:
        query_parts.append(f'search={search}')
    if category_id:
        query_parts.append(f'category_id={category_id}')
    if status:
        query_parts.append(f'status={status}')
    
    api_url = f'/api/products/export?{"&".join(query_parts)}'
    return redirect(api_url)


@products_routes.route('/products/<int:product_id>')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def view(product_id: int):
    """Render product view page with variants tab."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch product
    product = mediator.dispatch(GetProductByIdQuery(id=product_id))
    
    # Fetch variants for this product
    variants_query = GetVariantsByProductQuery(product_id=product_id, include_archived=False)
    variants = mediator.dispatch(variants_query)
    
    # Fetch price history for this product
    price_history_query = GetPriceHistoryQuery(product_id=product_id, limit=100)
    price_history = mediator.dispatch(price_history_query)
    
    # Fetch cost history for this product
    cost_history_query = GetCostHistoryQuery(product_id=product_id, limit=100)
    cost_history = mediator.dispatch(cost_history_query)
    
    return render_template(
        'products/view.html',
        product=product,
        variants=variants,
        price_history=price_history,
        cost_history=cost_history,
        locale=locale,
        direction=direction
    )


@products_routes.route('/products/<int:product_id>/variants')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_variants(product_id: int):
    """Render variants list page for a product."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch product
    product = mediator.dispatch(GetProductByIdQuery(id=product_id))
    
    # Fetch variants
    include_archived = request.args.get('include_archived', 'false').lower() == 'true'
    variants_query = GetVariantsByProductQuery(product_id=product_id, include_archived=include_archived)
    variants = mediator.dispatch(variants_query)
    
    return render_template(
        'products/variants_list.html',
        product=product,
        variants=variants,
        include_archived=include_archived,
        locale=locale,
        direction=direction
    )


@products_routes.route('/products/<int:product_id>/data/variants')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def get_variants_json(product_id: int):
    """Get variants JSON for a product (for Select2 in quote/order forms)."""
    try:
        variants_query = GetVariantsByProductQuery(product_id=product_id, include_archived=False)
        variants = mediator.dispatch(variants_query)
        
        # Convert to Select2 format
        items = []
        for variant in variants:
            items.append({
                'id': variant.id,
                'text': f"{variant.code} - {variant.name}",
                'code': variant.code,
                'name': variant.name,
                'price': float(variant.price) if variant.price else None
            })
        
        return jsonify({
            'results': items,
            'pagination': {
                'more': False
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'results': [],
            'pagination': {'more': False},
            'error': str(e)
        }), 500


@products_routes.route('/products/data/picker')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def get_products_picker_data():
    """Get products with variants and stock info for product picker modal."""
    try:
        from app.application.stock.queries.queries import GetStockLevelsQuery
        
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        # Get products
        products_query = ListProductsQuery(
            search=search if search else None,
            status='active',
            page=page,
            per_page=per_page
        )
        products = mediator.dispatch(products_query)
        
        # Calculate total count for pagination
        from app.domain.models.product import Product
        from app.infrastructure.db import get_session
        with get_session() as session:
            count_q = session.query(Product)
            if search:
                search_term = f"%{search}%"
                from sqlalchemy import or_
                count_q = count_q.filter(
                    or_(
                        Product.name.ilike(search_term),
                        Product.code.ilike(search_term),
                        Product.description.ilike(search_term)
                    )
                )
            count_q = count_q.filter(Product.status == 'active')
            total = count_q.count()
        
        # Build response with products and variants
        items = []
        for product in products:
            # Get variants for this product
            variants_query = GetVariantsByProductQuery(
                product_id=product.id,
                include_archived=False
            )
            variants = mediator.dispatch(variants_query)
            
            # Get total stock for product (sum across all locations and variants)
            stock_query = GetStockLevelsQuery(
                product_id=product.id,
                variant_id=None,  # Get all variants
                page=1,
                per_page=1000,  # Get all stock items
                include_zero=True
            )
            stock_items = mediator.dispatch(stock_query)
            total_stock = sum(Decimal(str(item.physical_quantity)) for item in stock_items)
            
            # Build variants info
            variants_info = []
            has_variants = len(variants) > 0
            for variant in variants:
                # Get stock for this variant
                variant_stock_query = GetStockLevelsQuery(
                    product_id=product.id,
                    variant_id=variant.id,
                    page=1,
                    per_page=1000,
                    include_zero=True
                )
                variant_stock_items = mediator.dispatch(variant_stock_query)
                variant_stock = sum(Decimal(str(item.physical_quantity)) for item in variant_stock_items)
                
                variants_info.append({
                    'id': variant.id,
                    'code': variant.code,
                    'name': variant.name,
                    'price': float(variant.price) if variant.price else None,
                    'stock': float(variant_stock)
                })
            
            # Determine variant attributes summary
            variant_attrs = []
            if has_variants:
                # Try to extract common attributes from variants
                # For now, just indicate that variants exist
                variant_attrs = ['Size', 'Color']  # This could be dynamic based on variant attributes
            
            items.append({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'price': float(product.price) if product.price else None,
                'stock': float(total_stock),
                'has_variants': has_variants,
                'variants': variants_info,
                'variant_attrs': variant_attrs if has_variants else []
            })
        
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        
        return jsonify({
            'items': items,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_more': page < total_pages
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'items': [],
            'error': str(e)
        }), 500


@products_routes.route('/products/<int:product_id>/variants/new')
@require_roles_or_redirect('admin', 'commercial')
def new_variant(product_id: int):
    """Render new variant form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch product
    product = mediator.dispatch(GetProductByIdQuery(id=product_id))
    
    return render_template(
        'products/variant_form.html',
        product=product,
        variant=None,
        locale=locale,
        direction=direction
    )


@products_routes.route('/variants/<int:variant_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit_variant(variant_id: int):
    """Render edit variant form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch variant
    variant = mediator.dispatch(GetVariantByIdQuery(id=variant_id))
    
    # Fetch product
    product = mediator.dispatch(GetProductByIdQuery(id=variant.product_id))
    
    return render_template(
        'products/variant_form.html',
        product=product,
        variant=variant,
        locale=locale,
        direction=direction
    )


@products_routes.route('/variants', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def save_variant():
    """Handle variant creation/update form submission."""
    try:
        variant_id = request.form.get('id', type=int)
        product_id = request.form.get('product_id', type=int)
        
        if variant_id:
            # Update existing variant
            command = UpdateVariantCommand(
                id=variant_id,
                name=request.form.get('name'),
                attributes=request.form.get('attributes'),
                price=Decimal(request.form['price']) if request.form.get('price') else None,
                cost=Decimal(request.form['cost']) if request.form.get('cost') else None,
                barcode=request.form.get('barcode') or None
            )
            mediator.dispatch(command)
            flash(_('Variant updated successfully'), 'success')
            return redirect(url_for('products_frontend.list_variants', product_id=product_id))
        else:
            # Create new variant
            command = CreateVariantCommand(
                product_id=product_id,
                code=request.form.get('code'),
                name=request.form.get('name'),
                attributes=request.form.get('attributes'),
                price=Decimal(request.form['price']) if request.form.get('price') else None,
                cost=Decimal(request.form['cost']) if request.form.get('cost') else None,
                barcode=request.form.get('barcode') or None
            )
            mediator.dispatch(command)
            flash(_('Variant created successfully'), 'success')
            return redirect(url_for('products_frontend.list_variants', product_id=product_id))
    except ValueError as e:
        flash(str(e), 'error')
        if variant_id:
            return redirect(url_for('products_frontend.edit_variant', variant_id=variant_id))
        else:
            return redirect(url_for('products_frontend.new_variant', product_id=product_id))
    except Exception as e:
        flash(_('An error occurred: {}').format(str(e)), 'error')
        if variant_id:
            return redirect(url_for('products_frontend.edit_variant', variant_id=variant_id))
        else:
            return redirect(url_for('products_frontend.new_variant', product_id=product_id))


@products_routes.route('/variants/<int:variant_id>/archive', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def archive_variant(variant_id: int):
    """Archive a variant."""
    try:
        variant = mediator.dispatch(GetVariantByIdQuery(id=variant_id))
        command = ArchiveVariantCommand(id=variant_id)
        mediator.dispatch(command)
        flash(_('Variant archived successfully'), 'success')
    except Exception as e:
        flash(_('Failed to archive variant: {}').format(str(e)), 'error')
    return redirect(url_for('products_frontend.list_variants', product_id=variant.product_id))


@products_routes.route('/variants/<int:variant_id>/activate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def activate_variant(variant_id: int):
    """Activate an archived variant."""
    try:
        variant = mediator.dispatch(GetVariantByIdQuery(id=variant_id))
        command = ActivateVariantCommand(id=variant_id)
        mediator.dispatch(command)
        flash(_('Variant activated successfully'), 'success')
    except Exception as e:
        flash(_('Failed to activate variant: {}').format(str(e)), 'error')
    return redirect(url_for('products_frontend.list_variants', product_id=variant.product_id))


@products_routes.route('/variants/<int:variant_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def delete_variant(variant_id: int):
    """Delete a variant."""
    try:
        variant = mediator.dispatch(GetVariantByIdQuery(id=variant_id))
        product_id = variant.product_id
        command = DeleteVariantCommand(id=variant_id)
        mediator.dispatch(command)
        flash(_('Variant deleted successfully'), 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(_('Failed to delete variant: {}').format(str(e)), 'error')
    return redirect(url_for('products_frontend.list_variants', product_id=product_id))


# ==================== Price List Routes ====================

@products_routes.route('/price-lists')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_price_lists():
    """Render price lists list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    is_active = request.args.get('is_active')
    if is_active is not None:
        is_active = is_active.lower() == 'true'
    
    # Fetch price lists via query
    query = ListPriceListsQuery(
        page=page,
        per_page=per_page,
        search=search,
        is_active=is_active
    )
    result = mediator.dispatch(query)
    
    return render_template(
        'products/price_lists_list.html',
        price_lists=result['items'],
        total=result['total'],
        page=result['page'],
        per_page=result['per_page'],
        search=search,
        is_active=is_active,
        locale=locale,
        direction=direction
    )


@products_routes.route('/price-lists/new')
@require_roles_or_redirect('admin', 'commercial')
def new_price_list():
    """Render new price list form."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    return render_template(
        'products/price_list_form.html',
        price_list=None,
        locale=locale,
        direction=direction
    )


@products_routes.route('/price-lists/<int:price_list_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit_price_list(price_list_id: int):
    """Render edit price list form."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch price list
    query = GetPriceListByIdQuery(id=price_list_id)
    price_list = mediator.dispatch(query)
    
    return render_template(
        'products/price_list_form.html',
        price_list=price_list,
        locale=locale,
        direction=direction
    )


@products_routes.route('/price-lists', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def save_price_list():
    """Save price list (create or update)."""
    price_list_id = request.form.get('id', type=int)
    
    try:
        if price_list_id:
            # Update existing
            command = UpdatePriceListCommand(
                id=price_list_id,
                name=request.form.get('name'),
                description=request.form.get('description'),
                is_active=request.form.get('is_active') == 'on'
            )
            mediator.dispatch(command)
            flash(_('Price list updated successfully'), 'success')
        else:
            # Create new
            command = CreatePriceListCommand(
                name=request.form.get('name'),
                description=request.form.get('description'),
                is_active=request.form.get('is_active', 'on') == 'on'
            )
            price_list = mediator.dispatch(command)
            price_list_id = price_list.id
            
            # Add products if provided during creation
            # Parse products from form data (format: products[0][product_id], products[0][price], etc.)
            form_dict = request.form.to_dict()
            products_to_add = {}
            
            # Extract product data from form
            for key, value in form_dict.items():
                if key.startswith('products[') and '][product_id]' in key:
                    # Extract index from key like "products[0][product_id]"
                    match = re.match(r'products\[(\d+)\]\[product_id\]', key)
                    if match:
                        index = match.group(1)
                        product_id = value
                        price_key = f'products[{index}][price]'
                        price = form_dict.get(price_key)
                        
                        if product_id and price:
                            products_to_add[index] = {
                                'product_id': int(product_id),
                                'price': Decimal(str(price))
                            }
            
            # Add products to price list
            for product_data in products_to_add.values():
                try:
                    add_command = AddProductToPriceListCommand(
                        price_list_id=price_list_id,
                        product_id=product_data['product_id'],
                        price=product_data['price']
                    )
                    mediator.dispatch(add_command)
                except ValueError as e:
                    # Skip duplicate products, continue with others
                    pass
                except Exception as e:
                    # Log error but continue
                    pass
            
            flash(_('Price list created successfully'), 'success')
        
        return redirect(url_for('products_frontend.list_price_lists'))
    except ValueError as e:
        flash(str(e), 'error')
        if price_list_id:
            return redirect(url_for('products_frontend.edit_price_list', price_list_id=price_list_id))
        else:
            return redirect(url_for('products_frontend.new_price_list'))
    except Exception as e:
        flash(_('Failed to save price list: {}').format(str(e)), 'error')
        if price_list_id:
            return redirect(url_for('products_frontend.edit_price_list', price_list_id=price_list_id))
        else:
            return redirect(url_for('products_frontend.new_price_list'))


@products_routes.route('/price-lists/<int:price_list_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def delete_price_list(price_list_id: int):
    """Delete a price list."""
    try:
        command = DeletePriceListCommand(id=price_list_id)
        mediator.dispatch(command)
        flash(_('Price list deleted successfully'), 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(_('Failed to delete price list: {}').format(str(e)), 'error')
    return redirect(url_for('products_frontend.list_price_lists'))


@products_routes.route('/price-lists/<int:price_list_id>/products')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_products_in_price_list(price_list_id: int):
    """Render products in price list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    
    # Fetch price list
    price_list_query = GetPriceListByIdQuery(id=price_list_id)
    price_list = mediator.dispatch(price_list_query)
    
    # Fetch products in price list
    query = GetProductsInPriceListQuery(
        price_list_id=price_list_id,
        page=page,
        per_page=per_page,
        search=search
    )
    result = mediator.dispatch(query)
    
    return render_template(
        'products/price_list_products.html',
        price_list=price_list,
        products=result['items'],
        total=result['total'],
        page=result['page'],
        per_page=result['per_page'],
        search=search,
        locale=locale,
        direction=direction
    )


@products_routes.route('/price-lists/<int:price_list_id>/products', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def save_product_to_price_list(price_list_id: int):
    """Add or update product in price list."""
    product_id = request.form.get('product_id', type=int)
    price = request.form.get('price', type=Decimal)
    action = request.form.get('action')  # 'add' or 'update'
    
    try:
        if action == 'add':
            command = AddProductToPriceListCommand(
                price_list_id=price_list_id,
                product_id=product_id,
                price=price
            )
            mediator.dispatch(command)
            flash(_('Product added to price list successfully'), 'success')
        elif action == 'update':
            command = UpdateProductPriceInListCommand(
                price_list_id=price_list_id,
                product_id=product_id,
                price=price
            )
            mediator.dispatch(command)
            flash(_('Product price updated successfully'), 'success')
        else:
            flash(_('Invalid action'), 'error')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(_('Failed to save product: {}').format(str(e)), 'error')
    
    return redirect(url_for('products_frontend.list_products_in_price_list', price_list_id=price_list_id))


@products_routes.route('/price-lists/<int:price_list_id>/products/<int:product_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def remove_product_from_price_list(price_list_id: int, product_id: int):
    """Remove product from price list."""
    try:
        command = RemoveProductFromPriceListCommand(
            price_list_id=price_list_id,
            product_id=product_id
        )
        mediator.dispatch(command)
        flash(_('Product removed from price list successfully'), 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(_('Failed to remove product: {}').format(str(e)), 'error')
    return redirect(url_for('products_frontend.list_products_in_price_list', price_list_id=price_list_id))


@products_routes.route('/price-lists/data/products')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def get_price_list_products_json():
    """Get products JSON for Select2 in price list modal. Returns active products only."""
    try:
        from app.application.products.queries.queries import ListProductsQuery
        
        query = ListProductsQuery(
            page=1,
            per_page=1000,
            status='active'
        )
        products = mediator.dispatch(query)
        
        # Convert to JSON format for Select2
        products_data = [
            {
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'text': f"{product.code} - {product.name}"  # Select2 format
            }
            for product in products
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'items': products_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_routes.route('/products/<int:product_id>/data/volume-pricing')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def get_volume_pricing_json(product_id: int):
    """Get volume pricing tiers JSON for product form. Returns tiers for a specific product."""
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
        
        return jsonify({
            'success': True,
            'data': {
                'items': items
            }
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_routes.route('/products/<int:product_id>/volume-pricing', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def save_volume_pricing(product_id: int):
    """Create or update a volume pricing tier for a product."""
    tier_id = request.form.get('id', type=int)
    min_quantity = Decimal(str(request.form.get('min_quantity')))
    max_quantity = request.form.get('max_quantity')
    max_quantity = Decimal(str(max_quantity)) if max_quantity else None
    price = Decimal(str(request.form.get('price')))
    
    try:
        if tier_id:
            # Update existing tier
            command = UpdateVolumePricingCommand(
                id=tier_id,
                min_quantity=min_quantity,
                max_quantity=max_quantity,
                price=price
            )
            mediator.dispatch(command)
            flash(_('Volume pricing tier updated successfully'), 'success')
        else:
            # Create new tier
            command = CreateVolumePricingCommand(
                product_id=product_id,
                min_quantity=min_quantity,
                price=price,
                max_quantity=max_quantity
            )
            mediator.dispatch(command)
            flash(_('Volume pricing tier created successfully'), 'success')
        
        return redirect(url_for('products_frontend.edit', product_id=product_id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('products_frontend.edit', product_id=product_id))
    except Exception as e:
        flash(_('Failed to save volume pricing tier: {}').format(str(e)), 'error')
        return redirect(url_for('products_frontend.edit', product_id=product_id))


@products_routes.route('/products/<int:product_id>/volume-pricing/<int:tier_id>', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_volume_pricing(product_id: int, tier_id: int):
    """Update a volume pricing tier (alternative route)."""
    return save_volume_pricing(product_id)


@products_routes.route('/products/<int:product_id>/volume-pricing/<int:tier_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def delete_volume_pricing(product_id: int, tier_id: int):
    """Delete a volume pricing tier."""
    try:
        command = DeleteVolumePricingCommand(id=tier_id)
        mediator.dispatch(command)
        flash(_('Volume pricing tier deleted successfully'), 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(_('Failed to delete volume pricing tier: {}').format(str(e)), 'error')
    
    return redirect(url_for('products_frontend.edit', product_id=product_id))


# ==================== Promotional Pricing Routes ====================

@products_routes.route('/products/<int:product_id>/data/promotional-prices')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def get_promotional_prices_json(product_id: int):
    """Get promotional prices JSON for product form. Returns all promotions for a specific product."""
    try:
        query = GetPromotionalPricesByProductQuery(product_id=product_id, include_expired=True)
        promotions = mediator.dispatch(query)
        
        items = [
            {
                'id': promo.id,
                'product_id': promo.product_id,
                'price': float(promo.price),
                'start_date': promo.start_date.isoformat() if promo.start_date else None,
                'end_date': promo.end_date.isoformat() if promo.end_date else None,
                'description': promo.description,
                'is_active': promo.is_active,
                'created_at': promo.created_at.isoformat() if promo.created_at else None,
                'updated_at': promo.updated_at.isoformat() if promo.updated_at else None,
                'created_by': promo.created_by
            }
            for promo in promotions
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'items': items
            }
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@products_routes.route('/products/<int:product_id>/promotional-prices', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def save_promotional_price(product_id: int):
    """Create or update a promotional price for a product."""
    promo_id = request.form.get('id', type=int)
    price = Decimal(str(request.form.get('price')))
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    description = request.form.get('description', '').strip()
    
    try:
        if promo_id:
            # Update existing promotion
            command = UpdatePromotionalPriceCommand(
                id=promo_id,
                price=price,
                start_date=start_date,
                end_date=end_date,
                description=description if description else None
            )
            mediator.dispatch(command)
            flash(_('Promotional price updated successfully'), 'success')
        else:
            # Create new promotion
            from flask_login import current_user
            created_by = current_user.id if current_user and current_user.is_authenticated else None
            
            command = CreatePromotionalPriceCommand(
                product_id=product_id,
                price=price,
                start_date=start_date,
                end_date=end_date,
                description=description if description else None,
                created_by=created_by
            )
            mediator.dispatch(command)
            flash(_('Promotional price created successfully'), 'success')
        
        return redirect(url_for('products_frontend.edit', product_id=product_id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('products_frontend.edit', product_id=product_id))
    except Exception as e:
        flash(_('Failed to save promotional price: {}').format(str(e)), 'error')
        return redirect(url_for('products_frontend.edit', product_id=product_id))


@products_routes.route('/products/<int:product_id>/promotional-prices/<int:promo_id>', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_promotional_price(product_id: int, promo_id: int):
    """Update a promotional price (alternative route)."""
    return save_promotional_price(product_id)


@products_routes.route('/products/<int:product_id>/promotional-prices/<int:promo_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def delete_promotional_price(product_id: int, promo_id: int):
    """Delete a promotional price."""
    try:
        command = DeletePromotionalPriceCommand(id=promo_id)
        mediator.dispatch(command)
        flash(_('Promotional price deleted successfully'), 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(_('Failed to delete promotional price: {}').format(str(e)), 'error')
    
    return redirect(url_for('products_frontend.edit', product_id=product_id))

