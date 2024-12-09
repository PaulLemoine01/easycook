// when click on a link with class 'clickable-row'

$(".clickable-row a").click(function (e) {
    e.stopPropagation();
})

$(".clickable-row").click(function (e) {
    if (e.target.type == "checkbox") {
        return;
    }
    // check if element has "nolink" class
    if ($(e.target).hasClass("nolink")) {
        return;
    }
    $(this).find(".loader").html("<i class=\"fa fa-circle-notch fa-spin\"></i>");
    if (!e.target.href) {
        var $a = $(this).find("a:not(.nolink)");
        var href = $a.attr("href");
        if (e.shiftKey || e.ctrlKey || e.metaKey || $a.attr('target') === '_blank') {
            window.open(href, '_blank');
        } else {
            window.location = href;
        }
    }
});


$(".notification").click(function () {
    $(this).remove()
})
var loc = window.location.pathname.split('?')[0];
$('.js-activated-link').each(function () {
    if ($(this).is('a')) {
        $(this).toggleClass('active', $(this).attr('href') == loc);
    } else {
        $(this).toggleClass('active', $(this).find("a").attr('href') == loc);
    }
});

// on searchform select or input or checkbox change, submit the form
$('#searchform select, #searchform input, #searchform checkbox').change(function () {
    $('#searchform').submit();
});


$(document).on('select2:open', (e) => {
    document.querySelector(`[aria-controls="select2-${e.target.id}-results"]`).focus();
});


$(".image-widget").change(function () {
    // show image preview in .image-widget-preview div above input
    var file = this.files[0];
    var reader = new FileReader();
    reader.onloadend = function (e) {
        $('.image-widget-preview').attr('src', reader.result);
    }
    if (file) {
        reader.readAsDataURL(file);
    }
})

$(".btn-load").click(function () {
    $(this).addClass("btn-loading");
})


// before leaving the page, show #loader
let loaderTimeout;

$(window).on('beforeunload', function () {
    clearTimeout(loaderTimeout);

    loaderTimeout = setTimeout(function () {
        $('#loader').show();
    }, 400);
});

$(window).focus(function () {
    clearTimeout(loaderTimeout);
    $('#loader').hide();
});

$(window).on('load', function () {
    clearTimeout(loaderTimeout);
    $('#loader').hide();
});

$(document).on('visibilitychange', function () {
    clearTimeout(loaderTimeout);
    if (document.visibilityState === 'visible') {
        $('#loader').hide();
    }
});
function initializeSelect2() {
    $("select:not([autoselect2]):not(.noselect2)").each(function () {
        var $select = $(this);

        if ($select.closest('.modal').length) {
            $select.select2({
                width: '100%',
                dropdownParent: $select.closest('.modal')
            });
        } else {
            $select.select2({
                width: '100%'
            });
        }
    });
}

initializeSelect2()
$(document).on('select2:open', (e) => {
    document.querySelector(`[aria-controls="select2-${e.target.id}-results"]`).focus();
});


$("select[autoselect2]").each(function () {
    var $select = $(this);

    var isInModal = $select.closest('.modal').length > 0;

    // Configuration select2
    var select2Config = {
        language: "fr",
        ajax: {
            delay: 250,
            data: function (params) {
                var query = {
                    search: params.term,
                    page: params.page || 1,
                }
                if ($(this).data("extraparams")) {
                    query = {...query, ...$(this).data("extraparams")};
                }
                return query;
            }
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        templateResult: function (data) {
            if (data.hasOwnProperty('html')) {
                return data.html;
            }
            return data.text;
        },
        width: '100%'
    };

    if (isInModal) {
        select2Config.dropdownParent = $select.closest('.modal');
    }

    $select.select2(select2Config);
});


// copy page title to <title> tag
$('title').html($('#pagetitle').html());


var fabnotify = function (type, message, clear) {
    if (clear) {
        $("#notifications").html("");
    }
    var html = `<div class="alert ${type} alert-dismissible">${message}   <a class="btn-close" data-bs-dismiss="alert" aria-label="close"></a></div>`;
    $("#notifications").append(html);
}

$('#selectall').click(function () {
    $('#visible_columns_form input[type=checkbox]').prop('checked', true);
    $("#visible_columns_form").submit();
});
$('#deselectall').click(function () {
    $('#visible_columns_form input[type=checkbox]').prop('checked', false);
    $("#visible_columns_form").submit();
});

$("#list_field_search").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    var words = value.split(' ');
    // filter list_field_table rows
    $("#list_field_table tr").filter(function () {
        // make AND logic between words
        $(this).toggle(words.every(word => $(this).text().toLowerCase().indexOf(word) > -1))
    });
});

function initializeDateRangePicker() {
    $(".daterange-picker").each(function () {
        var start_date = moment()
        var end_date = moment()
        if ($(this).val()) {
            start_date = $(this).val().split(" - ")[0]
            end_date = $(this).val().split(" - ")[1]
        }
        $(this).daterangepicker(
            {
                startDate: start_date,
                endDate: end_date,
                autoUpdateInput: false,
                ranges: {
                    '7 derniers jours': [moment().subtract(6, 'days'), moment()],
                    'Ce mois-ci': [moment().startOf('month'), moment()],
                    'Mois derniers': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
                    'Cette annee': [moment().startOf('year'), moment()]
                },
                opens: 'left',
                locale: {
                    "format": "DD/MM/YYYY",
                    "separator": " - ",
                    "applyLabel": "Appliquer",
                    "cancelLabel": "Effacer",
                    "fromLabel": "Du",
                    "toLabel": "Au",
                    "customRangeLabel": "Personnalisé",
                    "daysOfWeek": ["Di", "Lu", "Ma", "Me", "Je", "Ve", "Sa"],
                    "monthNames": ["Janvier", "Février", "Marc", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"],
                    "firstDay": 1
                }
            }
        );
        $(this).on('apply.daterangepicker', function (ev, picker) {
            $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
            $("#searchform").submit()
        });
        $(this).on('cancel.daterangepicker', function (ev, picker) {
            $(this).val('')
            $("#searchform").submit()
        });

    });
}

initializeDateRangePicker()
