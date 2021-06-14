$("#leftside-navigation .sub-menu > a").click(function (e) {
    $("#leftside-navigation ul ul").slideUp();
    $(this).next().is(":visible") || $(this).next().slideDown()

    $(this).find("i.arrow").toggleClass("toogle")
    $("#leftside-navigation a").not(this).find("i.arrow").removeClass("toogle")

    e.stopPropagation()
})

$('.sub-menu').each(function () {
    let $dropdownmenu = $(this)
    $(this).find('li').each(function () {
        if ($(this).find('a').attr('href') === location.pathname) {
            $dropdownmenu.find('ul').is(":visible") || $dropdownmenu.find('ul').slideDown()
            $dropdownmenu.find("i.arrow").toggleClass("toogle")
            $(this).find('a').css('color', '#18B495')
        }
    });
});