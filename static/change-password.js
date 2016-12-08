/**
 * SweetMates
 * change-passowrd.js
 * 
 * The necessary JavaScript to prevent accidential form submits on change_password.html
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
    $('#submitbutton').attr('disabled','disabled');
    
    // when character pressed in field
    $('#oldpassword').bind('keyup', function() {
        // get lengths of fields
        var oldpassword_length = $("#oldpassword").val().length;
        var password1_length = $("#password1").val().length;
        var password2_length = $("#password2").val().length;
        if (oldpassword_length > 0 && password1_length > 0 && password2_length > 0) {
            // if all fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
    // when character pressed in field
    $('#password1').bind('keyup', function() {
        // get lengths of fields
        var oldpassword_length = $("#oldpassword").val().length;
        var password1_length = $("#password1").val().length;
        var password2_length = $("#password2").val().length;
        if (oldpassword_length > 0 && password1_length > 0 && password2_length > 0) {
            // if all fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
    // when character pressed in field
    $('#password2').bind('keyup', function() {
        // get lengths of fields
        var oldpassword_length = $("#oldpassword").val().length;
        var password1_length = $("#password1").val().length;
        var password2_length = $("#password2").val().length;
        if (oldpassword_length > 0 && password1_length > 0 && password2_length > 0) {
            // if all fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
});