/**
 * SweetMates
 * chat.js
 * 
 * The necessary JavaScript to prevent accidential form submits on chat.html
 * 
 * Andrew Shackelford
 * ashackelford@college.harvard.edu
 * 
 * Eric Bornstein
 * ebornstein@college.harvard.edu
 * 
 * Catherine Tu
 * catherinetu@college.harvard.edu
 * 
 */

$(function(){
    // on DOM ready
    
    // disable submit button on load
    $('.mysubmitbutton').attr('disabled','disabled');
    
    // when character pressed in field
    $('.mychattext').bind('keyup', function() {
        // get length of field
        var chore_name_length = $(".mychattext").val().length;
        if (chore_name_length > 0) {
            // if field filled, enable button
            $('.mysubmitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('.mysubmitbutton').attr('disabled','disabled');
        }
    });
    
});