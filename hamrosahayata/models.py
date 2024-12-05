from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ADMIN = 'admin'
    CREATOR = 'creator'
    DONOR = 'donor'
    USER_TYPE_CHOICES = [
        (ADMIN, 'Admin'),
        (CREATOR, 'Creator'),
        (DONOR, 'Donor'),
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=DONOR,
        help_text="Role of the user in the crowdfunding platform"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Adding unique related_name for reverse relationships
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customuser_groups', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='customuser_permissions', 
        blank=True
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.get_user_type_display()})"

class Campaign(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.campaign.title}"

class Donation(models.Model):
    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='donations')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ONE_TIME = 'one-time'
    RECURRING = 'recurring'
    DONATION_TYPE_CHOICES = [
        (ONE_TIME, 'One-time'),
        (RECURRING, 'Recurring'),
    ]
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPE_CHOICES)
    thank_you_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} donated to {self.campaign.title}"

class Transaction(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='transaction')
    payment_method = models.CharField(max_length=50)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='completed')

    def __str__(self):
        return f"Transaction for Donation ID: {self.donation.id}"

class SocialMediaShare(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shares')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='shares')
    shared_at = models.DateTimeField(auto_now_add=True)
    referral_reward = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} shared {self.campaign.title}"

class Reward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rewards')
    points = models.IntegerField(default=0)
    activity = models.CharField(max_length=50)
    activity_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity} ({self.points} points)"

class AdminAction(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_actions')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='admin_actions')
    APPROVE = 'approve'
    REJECT = 'reject'
    FLAG = 'flag'
    ACTION_TYPE_CHOICES = [
        (APPROVE, 'Approve'),
        (REJECT, 'Reject'),
        (FLAG, 'Flag'),
    ]
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    feedback = models.TextField(null=True, blank=True)
    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} {self.action_type} campaign {self.campaign.title}"

class CampaignAccess(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='campaign_accesses')
    SILVER = 'silver'
    GOLD = 'gold'
    ACCESS_LEVEL_CHOICES = [
        (SILVER, 'Silver'),
        (GOLD, 'Gold'),
    ]
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES)
    MONEY = 'money'
    REWARD_POINTS = 'reward_points'
    UNLOCKED_BY_CHOICES = [
        (MONEY, 'Money'),
        (REWARD_POINTS, 'Reward Points'),
    ]
    unlocked_by = models.CharField(max_length=20, choices=UNLOCKED_BY_CHOICES)
    unlock_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.access_level} access unlocked by {self.unlocked_by}"