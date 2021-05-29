$("#leftside-navigation .sub-menu > a").click(function (e) {
    $("#leftside-navigation ul ul").slideUp();
    $(this).next().is(":visible") || $(this).next().slideDown();
    $(this).find("i.arrow").toggleClass("arrow fa fa-angle-down pull-right arrow fa fa-angle-up pull-right");
    e.stopPropagation()
})