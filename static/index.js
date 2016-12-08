/**
 * SweetMates
 * index.js
 * 
 * The necessary JavaScript to allow users to leave a group on index.html
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
    
    // called by button listener
    function leaveGroup() {
        // confirm dialog
        var r = confirm("Are you sure you want to leave this group?");
        if (r == true) {
            document.getElementById("leaveform").submit();
        }
    };
    // listener for leave button
    document.getElementById("leavebutton").addEventListener ("click", leaveGroup, false);
});