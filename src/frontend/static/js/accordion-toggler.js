$("#leftside-navigation .sub-menu > a").click(function (e) {
    $("#leftside-navigation ul ul").slideUp();
    $(this).next().is(":visible") || $(this).next().slideDown();

    $(this).find("i.arrow").toggleClass("toogle");
    $("#leftside-navigation a").not(this).find("i.arrow").removeClass("toogle")

    e.stopPropagation()
})