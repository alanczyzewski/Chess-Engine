jQuery(function(){
    if (session.color) {
        $('#' + session.color).click();
    }
    if (session.time) {
        $('#select-time').val(session.time);
    }
    
    sendGameAttributes();
});

$('.pieces-picker-box').click(function() {
    $('.pieces-picker-box').removeClass('selected-color');
    $(this).addClass('selected-color');
    sendGameAttributes();
});

$(".select-start-game").change(function() {
    sendGameAttributes();
});

function sendGameAttributes() {
    var color = $('.selected-color').attr('id');
    var time = $('#select-time').val();
    $.ajax(
    {
        type:"GET",
        url: "/update-game-attributes",
        data:{
            color: color,
            time: time
        },
        success: function( data ) 
        {
            console.log('success');
            console.log(data);
        }
    });
}
