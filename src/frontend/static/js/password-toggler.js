$('.eye').hover(function () {
    $(this).parent().siblings('input').attr('type', 'text');
    $(this).removeClass('eye fas fa-eye-slash').addClass('eye fas fa-eye')
}, function () {
    $(this).parent().siblings('input').attr('type', 'password');
    $(this).removeClass('eye fas fa-eye').addClass('eye fas fa-eye-slash')
})