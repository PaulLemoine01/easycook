import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView


logger = logging.getLogger("safeflataccess")


class CustomLoginRequiredMixin(LoginRequiredMixin):
    is_admin = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning("{user};{method};{get_full_path};403".format(user=request.user,
                                                                        method=request.method,
                                                                        get_full_path=request.get_full_path()))
            return self.handle_no_permission()

        if not request.user.is_admin and self.is_admin:
            logger.warning("{user};{method};{get_full_path};403".format(user=request.user,
                                                                        method=request.method,
                                                                        get_full_path=request.get_full_path()))
            return self.handle_no_permission()

        #if not 'subscription_status' in request.session:
        #    user = request.user
        #    if user.is_authenticated:
        #        if not "subscription_status" in request.session:
        #            if user.stripeSubscriptionId:
        #                try:
        #                    stripe.api_key = settings.STRIPE_SECRET_KEY
        #                    subscription = stripe.Subscription.retrieve(user.stripeSubscriptionId)
        #                    request.session['subscription_status'] = True
        #                    if not subscription.status == 'active':
        #                        user.stripeSubscriptionId = None
        #                        user.save()
        #                        request.session['subscription_status'] = False
#
        #                except stripe.error.StripeError as e:
        #                    # Handle Stripe API errors
        #                    print(f"Stripe error: {e}")

        logger.info("{user};{method};{get_full_path};200".format(user=request.user,
                                                                 method=request.method,
                                                                 get_full_path=request.get_full_path()))
        return super().dispatch(request, *args, **kwargs)


class CustomCreateView(CustomLoginRequiredMixin, CreateView):
    pass


class CustomUpdateView(CustomLoginRequiredMixin, UpdateView):
    pass


class CustomDeleteView(CustomLoginRequiredMixin, DeleteView):
    pass


class CustomListView(CustomLoginRequiredMixin, ListView):
    pass


class CustomDetailView(CustomLoginRequiredMixin, DetailView):
    pass


class CustomView(CustomLoginRequiredMixin, View):
    pass
