/* Javascript for UcDockerXBlock. */
function UcDockerXBlock(runtime, element) {

    var handlerSaveUrl = runtime.handlerUrl(element, 'create_lab');
    var handlerDetailUrl = runtime.handlerUrl(element, 'get_lab');

    function saveLabCallback(response) {
        if (response.result == true) {
            window.location.reload(true);
        } else {
            $('.error-message', element).html('Error: ' + response.message);
        }
    }

    function showLabDetailCallback(result) {
        if (result.result == true) {
            $("#lab_name_d", element).attr('value', result.name);
            $("#lab_desc_d", element).text(result.desc);
            $("#lab_project_d", element).text(result.project);
            $("#lab_docker_file_d", element).text(result.dockerfile);
            $("#lab_make_scripts_d", element).text(result.makescripts);
        }
    }

    $('.show_detail_btn', element).click(function(eventObject) {
        params = {
            "name": eventObject.target.name
        };
        $.ajax({
            type: "POST",
            url: handlerDetailUrl,
            data: JSON.stringify(params),
            success: showLabDetailCallback
        });
    });

    $('.save-button', element).bind('click', function() {
        params = {
            "name": $("#lab_name", element).val(),
            "desc": $("#lab_desc", element).val(),
            "project": $("#lab_project", element).val(),
            "dockerfile": $("#lab_docker_file", element).val(),
            "makescripts": $("#lab_make_scripts", element).val()
        };
        $.ajax({
            type: "POST",
            url: handlerSaveUrl,
            data: JSON.stringify(params),
            success: saveLabCallback
        });
        $('.error-message', element).html();
    });

    $('.cancel-button', element).bind('click', function() {
        runtime.notify('cancel', {});
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}