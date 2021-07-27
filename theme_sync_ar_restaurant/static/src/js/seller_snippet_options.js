odoo.define('theme_ar_fashion.snippet_bestsellers_options', function (require) {
    'use strict';

    require('web.dom_ready');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var rpc = require('web.rpc');


    options.registry.snippet_bestsellers_options = options.Class.extend({
        onBuilt: function () {
			alert('ssssssssssssssssssss');
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

  
});

//todo product_list['val]  ,