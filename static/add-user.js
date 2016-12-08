/**
 * SweetMates
 * add-user.js
 * 
 * The necessary JavaScript to prevent accidential form submits on add-user.html
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
    // ON DOM ready
    
    // disable submit button on load
    $('#submitbutton').attr('disabled','disabled');
    
    // when character pressed in field
    $('#joincode').bind('keyup', function() {
        // get length of field
        $('#submitbutton').attr('disabled','disabled');
        var join_code_length = $("#joincode").val().length;
        if (join_code_length > 0) {
            // if field filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
});
