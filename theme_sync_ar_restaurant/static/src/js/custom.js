odoo.define('theme_ar_fashion.custom_js', function (require) {
    "use strict";
    require('web.dom_ready');

    var featured_slider = {
        dots: true,
        infinite: false,
        speed: 300,
        slidesToShow: 4,
        arrows: false,
        slidesToScroll: 4,
        responsive: [
            {
                breakpoint: 1026,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3
                }
            },
            {
                breakpoint: 769,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            },
            {
                breakpoint: 767,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            }
        ]
    };
    var dealweekSlider = {
        dots: true,
        infinite: false,
        speed: 300,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false
    };

    var topFeaturedSlider = {
        dots: true,
        infinite: false,
        speed: 300,
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false
    };

    var snippet_sellers = $('.seller-snippet');
    snippet_sellers.each(function () {
        var snippet_seller = $(this);
        var category_id = snippet_seller.data('active-categ') || 13;
        /*var category_id = 13;*/
        console.log(category_id, snippet_seller);
        if (!snippet_seller.hasClass('syncoria-snippet-initialized')) {
            snippet_seller.addClass('syncoria-snippet-initialized');
            $.ajax({
                type: "get",
                url: "/syncoria/category/" + category_id,
                success: function (response) {
                    snippet_seller.html(response);
                    /*snippet_seller.find(".custom-slider").slick({
                        dots: true,
                        infinite: false,
                        speed: 300,
                        slidesToShow: 1,
                        slidesToScroll: 1,
                        arrows: false
                    });*/
                },
                error: function (returnval) {
                    // product_list.html('<div>Unable to connect with server.</div>');
                }
            });
        }
    });

    if ($(".custom-svg").length > 0) {
        $('img.custom-svg').each(function () {
            var $img = $(this);
            var imgURL = $img.attr('src');

            $.get(imgURL, function (data) {
                // Get the SVG tag, ignore the rest
                var $svg = $(data).find('svg');
                // Replace image with new SVG
                $img.replaceWith($svg);
            });
        });
    }
    /* dropdown menu in bootstrap start*/
    $('.dropdown-menu a.dropdown-toggle').on('click', function (e) {
        if (!$(this).next().hasClass('show')) {
            $(this).parents('.dropdown-menu').first().find('.show').removeClass("show");
        }
        var $subMenu = $(this).next(".dropdown-menu");
        var $subMenu1 = $(this).closest(".dropdown");
        $subMenu1.toggleClass('show');
        $subMenu.toggleClass('show');

        $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function (e) {
            $('.dropdown-submenu .show').removeClass("show");
        });

        return false;
    });
    /* dropdown menu in bootstrap end*/
    /*off canvas navigation start*/

    if ($(".off-canvas-nav-list").length > 0) {
        $(".off-canvas-nav-list").mCustomScrollbar({
            axis: "y",
            theme: "dark-3"
        });
    }
    $(document).on("click", ".navbar-toggle-hamburger", function (e) {
        e.preventDefault();
        $(this).closest(".off-canvas-navigation-wrapper").toggleClass("toggled");
        $("body").addClass("off-canvas-active");
    });
    $(document).on("click", ".navbar-toggle-close", function (e) {
        e.preventDefault();
        $(this).closest(".off-canvas-navigation-wrapper").removeClass("toggled");
        $("body").removeClass("off-canvas-active");
    });
    $('html').click(function (e) {
        if (!$(e.target).is('off-canvas-active') &&
            (!$(e.target).parents().hasClass('off-canvas-navigation-wrap')) &&
            (!$(e.target).hasClass('off-canvas-navigation-wrap'))) {
            $("body").removeClass('off-canvas-active');
            $(".off-canvas-navigation-wrapper").removeClass("toggled");
        }
    });

    /*off canvas navigation end */
    if (navigator.userAgent.indexOf('Mac') > 0)
        $('body').addClass('mac-os');
    if (navigator.userAgent.indexOf('Safari') > 0)
        $('body').addClass('safari');
    if (navigator.userAgent.indexOf('Chrome') > 0)
        $('body').addClass('chrome');
    if (navigator.userAgent.indexOf('Mac') > 0)
        $('body').addClass('mac-os');
    if (navigator.userAgent.indexOf('Safari') > 0)
        $('body').addClass('safari');
    if (navigator.userAgent.indexOf('Chrome') > 0)
        $('body').addClass('chrome');

    /* slick slider for details page start */
    let page_product_id = $('.js_product').find('.product_id').val();
    $('.slider-for > div, .slider-nav > div').each(function (index, slide) {
        let variant_id = $('.img-variant', slide).attr('img-variant-id');
        if (variant_id && variant_id !== page_product_id) {
            $(slide).removeClass('slider-item');
            $(slide).hide();
        } else {
            $(slide).addClass('slider-item');
            $(slide).show();
        }
    });
	/*
    $('.slider-for').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        fade: true,
        asNavFor: '.slider-nav',
        rows: 0,
        slide: '.slider-item'
    });
	
    $('.slider-nav').slick({
        slidesToShow: 5,
        slidesToScroll: 1,
        asNavFor: '.slider-for',
        dots: false,
        centerMode: false,
        focusOnSelect: true,
        rows: 0,
        slide: '.slider-item'
    });*/
    // let page_product_id = $('.js_product').find('.product_id').val();
    // $('.slider-nav').slick('slickFilter', function(index, slide) {
    //     let variant_id = $('.img-variant', slide).attr('img-variant-id');
    //     if(!variant_id || variant_id === page_product_id){
    //         return true;
    //     }
    //     else {
    //         return false;
    //     }
    // });
    // $('.slider-for').slick('slickFilter', function(index, slide) {
    //     let variant_id = $('.img-variant', slide).attr('img-variant-id');
    //     if(!variant_id || variant_id === page_product_id){
    //         return true;
    //     }
    //     else {
    //         return false;
    //     }
    // });
    //TODO zoom removal
    // if ($(window).width() > 767) {
    //     $('.slider-preview-wrap').zoom({on: 'click'});
    // }


    /* slick slider for details page end */

    if (!$('.recent-view-slider').hasClass('slick-initialized')) {
        $('.recent-view-slider').slick({
            responsive: [
                {
                    breakpoint: 1026,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                },
                {
                    breakpoint: 767,
                    settings: {
                        slidesToShow: 1,
                        slidesToScroll: 1
                    }
                }
            ]
        });
    }
    if (!$('.featured-slider').hasClass('slick-initialized')) {
        $('.featured-slider').slick({
            dots: true,
            infinite: false,
            speed: 300,
            slidesToShow: 4,
            arrows: false,
            slidesToScroll: 4,
            responsive: [
                {
                    breakpoint: 1026,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                },
                {
                    breakpoint: 769,
                    settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2
                    }
                },
                {
                    breakpoint: 767,
                    settings: {
                        slidesToShow: 1,
                        slidesToScroll: 1
                    }
                }
            ]
        });
    }
    if (!$('.brand-slider').hasClass('slick-initialized')) {
        $('.brand-slider').slick({
            dots: false,
            infinite: false,
            speed: 300,
            slidesToShow: 5,
            arrows: true,
            slidesToScroll: 5,
            responsive: [
                {
                    breakpoint: 1026,
                    settings: {
                        slidesToShow: 4,
                        slidesToScroll: 4
                    }
                },
                {
                    breakpoint: 767,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                }
            ]
        });
    }
    if (!$('.custom-slider').hasClass('slick-initialized')) {
        $('.custom-slider').slick({
            dots: true,
            infinite: false,
            speed: 300,
            slidesToShow: 1,
            slidesToScroll: 1,
            arrows: false
        });
    }
    $(".switch-grid-list").on("click", function () {
        var view = $(this).data("view");
        if (!$("#products_grid > div").hasClass("custom-switch-view-" + view)) {
            $("#products_grid > div").removeClass();
            $("#products_grid > div").addClass("custom-switch-view-" + view + " clearfix");
            $.ajax({
                type: "get",
                url: "/shop/change_shop_view/custom-switch-view-" + view,
            });
        }
    });
    if ($('.next-page-link').length > 0 && $('.custom-switch-view-grid,.custom-switch-view-list')) {
        $('.custom-switch-view-grid,.custom-switch-view-list').infiniteScroll({
            path: '.next-page-link',
            append: '.oe_product',
            status: '.page-load-status',
            hideNav: '.pagination',
        });
    }
    $('.search-category-select a').on('click', function (e) {
        e.preventDefault();
        $("#searchbar_form").attr('action', $(e.target).data('action')).submit();
    })

    _.each($('.product-radio-filter'), function (filter) {
        var list = $("ul>li", filter);
        var numToShow = 8;
        var viewMore = $(".view-more", filter);
        var numInList = list.length;
        list.hide();
        viewMore.hide();
        if (numInList > numToShow) {
            viewMore.show();
        }
        list.slice(0, numToShow).show();
        viewMore.click(function (e) {
            e.preventDefault();
            if (list.filter(':hidden').length) {
                list.slideDown();
                $(this).text('View Less').addClass('view-less');
            } else {
                list.slice(numToShow).slideUp();
                $(this).text('View More').removeClass('view-less');
                $('strong', filter).get(0).scrollIntoView({behavior: "smooth"});
            }
        });
    });

});

odoo.define('theme_ar_fashion.ProductConfiguratorMixin', function (require) {
    'use strict';
    require('web.dom_ready');
    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.WebsiteSale.include({
        _updateProductImage: function ($productContainer, productId, productTemplateId, new_carousel, isCombinationPossible) {
            this._super($productContainer, productId, productTemplateId, new_carousel, isCombinationPossible);
            $('.slider-for, .slider-nav').slick('unslick');
            $('.slider-for > div, .slider-nav > div').each(function (index, slide) {
                let variant_id = $('.img-variant', slide).attr('img-variant-id');
                if (variant_id && parseInt(variant_id) !== productId) {
                    $(slide).removeClass('slider-item');
                    $(slide).hide();
                } else {
                    $(slide).addClass('slider-item');
                    $(slide).show();
                }
            });
            $('.slider-for').slick({
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: false,
                fade: true,
                asNavFor: '.slider-nav',
                rows: 0,
                slide: '.slider-item'
            });
            $('.slider-nav').slick({
                slidesToShow: 5,
                slidesToScroll: 1,
                asNavFor: '.slider-for',
                dots: false,
                centerMode: false,
                focusOnSelect: true,
                rows: 0,
                slide: '.slider-item'
            });
        }
    });
});
