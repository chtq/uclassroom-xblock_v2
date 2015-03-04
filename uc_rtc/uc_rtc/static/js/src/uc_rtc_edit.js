function UcRtcXBlock(runtime, element) {
    $(function ($) {
        /* Here's where you'd do things on page load. */
    });

    $('.cancel-button', element).bind('click', function() {
        runtime.notify('cancel', {});
    });
}