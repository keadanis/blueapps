odoo.define('theme_syncoria_electronics.snippet_bestsellers_options', function (require) {
    'use strict';

    require('web.dom_ready');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var rpc = require('web.rpc');


    options.registry.snippet_bestsellers_options = options.Class.extend({
        onBuilt: function () {
            var self = this;
            return wUtils.prompt({
                window_title: "Add a Seller Snippet",
                select: "Category",
                init: function () {
                    return rpc.query({
                        'model': 'product.public.category',
                        'method': 'search_read',
                        'fields': ['name']
                    }).then(function (categories) {
                        return _.map(categories, category => [category.id, category.name]);
                    })
                }
            }).then(function (category) {
                self.$target.find('.seller-snippet').attr("data-active-categ", category['val']);
            });
        },
    });

    options.registry.snippet_productlist_options = options.Class.extend({
        onBuilt: function () {
            this.id = 'productlist_' + new Date().getTime();
            this.$target.attr('data-id', this.id);
            this.addProductList();
        },
        addProductList: function () {
            var self = this;
            return wUtils.prompt({
                window_title: "Add a Product List",
                select: "Product List",
                init: function () {
                    return rpc.query({
                        'model': 'syncoria.product.list',
                        'method': 'search_read',
                        'fields': ['name']
                    }).then(function (product_lists) {
                        return _.map(product_lists, product_list => [product_list.id, product_list.name]);
                    });
                }
            }).then(product_list => {
                var product_lists = self.$target.data("product-lists");
                if (product_lists) {
                    product_lists = product_lists + ',' + product_list;
                } else {
                    product_lists = product_list;
                }
                self.$target.attr("data-product-lists", product_lists['val']);
            });
        }
    });

    options.registry.snippet_top_featured_options = options.Class.extend({

        onBuilt: function () {
            this.addTopProductList();
        },
        addTopProductList: function () {
            var self = this;
            return wUtils.prompt({
                window_title: "Add a Product List",
                select: "Product List",
                init: function () {
                    return rpc.query({
                        'model': 'syncoria.product.list',
                        'method': 'search_read',
                        'fields': ['name']
                    }).then(function (product_lists) {
                        return _.map(product_lists, product_list => [product_list.id, product_list.name]);
                    });
                }
            }).then(product_list => {
                self.$target.attr("data-product-list", product_list['val']);
            });
        },
        slickNext: function () {
            this.$target.find('.slick-slider').slick('slickNext');
        },
        slickRemove: function () {
            var slide = this.$target.find('.slick-slider');
            slide.slick('slickRemove', slide.slick('slickCurrentSlide'));
        },
        slickPrev: function () {
            this.$target.find('.slick-slider').slick('slickPrev');
        },
        slickAdd: function () {
            var slide = this.$target.find('.slick-slider');
            // var current = this.$target.find('.slick-slider').slick('slickCurrentSlide');
            // this.$target.find('.slick-slider').slick('slickAdd',slide.$slides[current]);
            if (slide.hasClass('slick-initialized')) {
                slide.slick('unslick');
            }
            var html = `<div>
    <div class="item">
        <img src="/theme_syncoria_electronics/static/src/images/top-img.png" alt="preview"/>
        <div class="item-info">
            <h2>Heading Line</h2>
            <p>Simple texts</p>
            <div class="bottom-price-button">
                <div class="price-value">$
                    <span>592</span>
                </div>
                <a href="#" class="btn btn-primary">Buy Now</a>
            </div>
        </div>
    </div>
</div>`;
            slide.append(html);
            slide.slick({
                dots: true,
                infinite: false,
                speed: 300,
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: false
            });
        },
    });

    options.registry.snippet_dealweek_options = options.Class.extend({
        onBuilt: function () {
            this.changeProductList();
        },
        changeProductList: function () {
            var self = this;
            return wUtils.prompt({
                window_title: "Change Product List",
                select: "Product List",
                init: function () {
                    return rpc.query({
                        'model': 'syncoria.product.list',
                        'method': 'search_read',
                        'fields': ['name']
                    }).then(function (product_lists) {
                        return _.map(product_lists, product_list => [product_list.id, product_list.name]);
                    });
                }
            }).then(product_list => {
                console.log(product_list['val']);
                self.$target.attr("data-product-list", product_list['val']);
            });
        }
    });

});

//todo product_list['val]  ,