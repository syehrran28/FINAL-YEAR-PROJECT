$(document).ready(function () {
    $('.sign_in').click(function () {
        $('.login').addClass('active');
        $('.welcome').addClass('active');
        $('.sign_up').addClass('active');
    });

    $('.btn').click(function () {
        $('.sign_up').removeClass('active');
        $('.login').removeClass('active');
        $('.welcome').removeClass('active');
    });
});
