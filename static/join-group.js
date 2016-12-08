/**
 * SweetMates
 * join-group.js
 * 
 * The necessary JavaScript to prevent accidential form submits on join-group.html
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
    $('#groupcode').bind('keyup', function() {
        // get length of fields
        var group_code_length = $("#groupcode").val().length;
        var join_code_length = $("#joincode").val().length;
        if (group_code_length > 0 && join_code_length > 0) {
            // if all fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
    // when character pressed in field
    $('#joincode').bind('keyup', function() {
        // get length of fields
        var group_code_length = $("#groupcode").val().length;
        var join_code_length = $("#joincode").val().length;
        if (group_code_length > 0 && join_code_length > 0) {
            // if all fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
});