$(document).ready(function () {
    $(".filter-year").yearFilterPagination({
        itemsPerPage: 20
    });
});


(function ($) {
    $.fn.yearFilterPagination = function (options) {
        const settings = $.extend({
            itemsPerPage: 20,
            itemSelector: ".year-list li",
            paginationSelector: ".custom_pagination ul",
            startPage: 1
        }, options);

        return this.each(function () {
            const $container = $(this);
            const $items = $container.find(settings.itemSelector).not('.no-pagination');
            const $pagination = $(settings.paginationSelector);
            let currentPage = settings.startPage;
            const totalPages = Math.ceil($items.length / settings.itemsPerPage);

            function updateView() {
                // Show correct items
                $items.hide();
                const start = (currentPage - 1) * settings.itemsPerPage;
                $items.slice(start, start + settings.itemsPerPage).show();

                // Show all pagination links
                $pagination.find("li").show();

                updatePaginationControls();
            }

            function updatePaginationControls() {
                $pagination.find("li").removeClass("disabled").removeAttr("aria-disabled").removeAttr("aria-current");

                // Disable First/Prev if on page 1
                if (currentPage === 1) {
                    $pagination.find("li:contains('First'), li:contains('Previous')")
                        .addClass("disabled").attr("aria-disabled", "true");
                }

                // Disable Next/Last if on last page
                if (currentPage === totalPages) {
                    $pagination.find("li:contains('Next'), li:contains('Last')")
                        .addClass("disabled").attr("aria-disabled", "true");
                }

                // Set aria-current on current page number
                $pagination.find("li").each(function () {
                    const text = $(this).text().trim();
                    if (parseInt(text) === currentPage) {
                        $(this).attr("aria-current", "page");
                    }
                });
            }

            function goToPage(page) {
                if (page >= 1 && page <= totalPages) {
                    currentPage = page;
                    updateView();
                }
            }

            $pagination.on("click", "a", function (e) {
                e.preventDefault();
                const $parent = $(this).parent();
                if ($parent.hasClass("disabled")) return;

                const text = $(this).text().trim().toLowerCase();
                switch (text) {
                    case "first":
                        goToPage(1);
                        break;
                    case "previous":
                        goToPage(currentPage - 1);
                        break;
                    case "next":
                        goToPage(currentPage + 1);
                        break;
                    case "last":
                        goToPage(totalPages);
                        break;
                    default:
                        const num = parseInt(text);
                        if (!isNaN(num)) goToPage(num);
                }
            });

            updateView(); // Initial call
        });
    };
})(jQuery);
