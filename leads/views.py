from unicodedata import category
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, reverse
from .models import Lead, Agent, Category
from .forms import LeadForm, LeadModelForm, CustomUserCreation, AssignAgentForm, LeadCategoryUpdateForm
from agents.mixins import OrganizerAndLoginRequiredMixin
# CRUD+L - Create, Retrieve, Update and Delete + List View

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreation
    
    def get_success_url(self):
        return reverse("login")


# Template
class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

def landing_page(request):
    return render(request, 'landing.html')

#  List View
class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads" # Customizing object name
    
    def get_queryset(self):
        user = self.request.user
        # Initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, 
                agent__isnull=False
                )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation, 
                agent__isnull=False
                ) 
            # Filter for the agent that is logged
            queryset = queryset.filter(agent__user=user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, 
                agent__isnull=True
                )
            context.update({
            "unassigned_leads": queryset
        })
        return context
           
            
        

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        'leads': leads
    }
    return render(request, 'leads/lead_list.html', context)

# Detail View
class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    queryset = Lead.objects.all()
    context_object_name = "lead" # Customizing object name

    def get_queryset(self):
        user = self.request.user

        # Initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation) 
            # Filter for the agent that is logged
            queryset = queryset.filter(agent__user=user)
        
        return queryset

def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead": lead
    }
    return render(request, 'leads/lead_detail.html', context)    

# Create View 
class LeadCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm
    
    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        # Todo send Email
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to thie site to see the new lead",
            from_email="test@test.com",
            recipient_list=["brancore87@gmail.com"]
        )
        return super(LeadCreateView, self).form_valid(form)

# Django Model Form
def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        print("Receiving a post request")
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            print('The lead has been created')
            return redirect('/leads')
    context = {
        "form": LeadModelForm()
    }
    return render(request, 'leads/lead_create.html', context)
 

# Update View
class LeadUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    queryset = Lead.objects.all()
    form_class = LeadModelForm
    
    def get_queryset(self):
        user = self.request.user
        # Initial queryset of leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)
        

    def get_success_url(self):
        return reverse("leads:lead-list")

def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        print("Receiving a post request")
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            print('The lead has been created')
            return redirect('/leads')
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, 'leads/lead_update.html', context)  


# Delete View
class LeadDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"

    def get_success_url(self):
        return reverse("leads:lead-list")

    def get_queryset(self):
        user = self.request.user
        # Initial queryset of leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    if lead.delete():
        print('This lead is deleted')
        return redirect('/leads')


class AssignAgentView(OrganizerAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request 
        })
        return kwargs

    def get_success_url(self):
            return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent 
        lead.save()
        return super(AssignAgentView, self).form_valid(form)
        

class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
                )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
                ) 
        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context 

    def get_queryset(self):
        user = self.request.user
        # Initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Category.objects.filter(
                organisation=user.userprofile
                )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
                ) 
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    # def get_context_data(self, **kwargs):
    #     context = super(CategoryDetailView, self).get_context_data(**kwargs)
    #     leads = self.get_object().leads.all()
    #     context.update({
    #         "leads": leads
    #     })
    #     return context

    def get_queryset(self):
        user = self.request.user
        # Initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Category.objects.filter(
                organisation=user.userprofile
                )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
                ) 
        return queryset

class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # Initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation) 
            # Filter for the agent that is logged
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})











# Edit and Update detail form
# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == "POST":
#         print("Receiving a post request")
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             print("The form is valid")
#             print(form.cleaned_data)
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             lead.first_name = first_name
#             lead.last_name = last_name
#             lead.age = age
#             lead.save()
#             print('The lead has been updated')
#             return redirect('/leads')
    # context = {
    #     "form": form,
    #     "lead": lead
    # }
    # return render(request, 'leads/lead_update.html', context)    


# Django Form
# def lead_create(request):
    # form = LeadForm()
    # if request.method == "POST":
    #     print("Receiving a post request")
    #     form = LeadForm(request.POST)
    #     if form.is_valid():
    #         print("The form is valid")
    #         print(form.cleaned_data)
    #         first_name = form.cleaned_data['first_name']
    #         last_name = form.cleaned_data['last_name']
    #         age = form.cleaned_data['age']
    #         agent = form.cleaned_data['agent']
    #         Lead.objects.create(
    #             first_name=first_name, 
    #             last_name=last_name, 
    #             age=age, 
    #             agent=agent
    #             )
    #         print('The lead has been created')
    #         return redirect('/leads')
    # context = {
    #     "form": LeadForm()
    # }
#     return render(request, 'leads/lead_create.html', context) 