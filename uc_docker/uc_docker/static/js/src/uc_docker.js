/* Javascript for UcDockerXBlock. */
function UcDockerXBlock(runtime, element) {

    var createDockerHandlerUrl = runtime.handlerUrl(element, 'create_docker');
    var startDockerHandlerUrl = runtime.handlerUrl(element, 'run_docker');
    var stopDockerHandlerUrl = runtime.handlerUrl(element, 'stop_docker');

    function jsCallback(response) {
        if (response.result == true) {
            window.location.reload(true);
        } else {
            $('.error-message', element).html('Error: ' + response.message);
        }
    }

    $('#create_docker_btn', element).click(function(eventObject) {
        params = {
            "name": $("#docker_name", element).val(),
            "lab": $("#docker_lab", element).val()
        };
        $.ajax({
            type: "POST",
            url: createDockerHandlerUrl,
            data: JSON.stringify(params),
            success: jsCallback
        });
        $('.error-message', element).html();
    });

    $('.start_docker_btn', element).click(function(eventObject) {
        params = {
            "name": eventObject.target.name
        };
        $.ajax({
            type: "POST",
            url: startDockerHandlerUrl,
            data: JSON.stringify(params),
            success: jsCallback
        });
    });

    $('.stop_docker_btn', element).click(function(eventObject) {
        params = {
            "name": eventObject.target.name
        };
        $.ajax({
            type: "POST",
            url: stopDockerHandlerUrl,
            data: JSON.stringify(params),
            success: jsCallback
        });
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}