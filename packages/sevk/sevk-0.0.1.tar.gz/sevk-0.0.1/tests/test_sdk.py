"""
Sevk Python SDK Integration Tests
"""

import pytest
import uuid


class TestAuthentication:
    """Test authentication"""

    def test_should_reject_invalid_api_key(self, sevk_class):
        """Should reject invalid API key"""
        from sevk import Sevk, SevkOptions
        options = SevkOptions(base_url="http://localhost:4000")
        invalid_sevk = Sevk("sevk_invalid_api_key_12345", options)
        with pytest.raises(Exception) as exc_info:
            invalid_sevk.contacts.list()
        assert "401" in str(exc_info.value)

    def test_should_reject_empty_api_key(self, sevk_class):
        """Should reject empty API key"""
        from sevk import Sevk, SevkOptions
        options = SevkOptions(base_url="http://localhost:4000")
        empty_sevk = Sevk("", options)
        with pytest.raises(Exception) as exc_info:
            empty_sevk.contacts.list()
        # Empty API key causes either 401 or header error
        error_msg = str(exc_info.value).lower()
        assert "401" in str(exc_info.value) or "header" in error_msg or "illegal" in error_msg

    def test_should_reject_malformed_api_key(self, sevk_class):
        """Should reject malformed API key (not starting with sevk_)"""
        from sevk import Sevk, SevkOptions
        options = SevkOptions(base_url="http://localhost:4000")
        malformed_sevk = Sevk("invalid_key_format", options)
        with pytest.raises(Exception) as exc_info:
            malformed_sevk.contacts.list()
        assert "401" in str(exc_info.value)


class TestContacts:
    """Test contacts resource"""

    def test_should_list_contacts(self, sevk):
        """Should list contacts with correct response structure"""
        response = sevk.contacts.list()
        assert "items" in response
        assert "total" in response
        assert "page" in response
        assert "totalPages" in response
        assert isinstance(response["items"], list)

    def test_should_list_contacts_with_pagination(self, sevk):
        """Should list contacts with pagination"""
        response = sevk.contacts.list(page=1, limit=5)
        assert response["page"] == 1
        assert len(response["items"]) <= 5

    def test_should_create_contact(self, sevk):
        """Should create a contact with required fields"""
        email = f"test-{uuid.uuid4()}@example.com"
        contact = sevk.contacts.create(email=email)
        assert contact["email"] == email
        assert "id" in contact
        # Cleanup
        sevk.contacts.delete(contact["id"])

    def test_should_get_contact(self, sevk):
        """Should get a contact by id"""
        email = f"test-{uuid.uuid4()}@example.com"
        created = sevk.contacts.create(email=email)
        contact = sevk.contacts.get(created["id"])
        assert contact["id"] == created["id"]
        assert contact["email"] == email
        # Cleanup
        sevk.contacts.delete(created["id"])

    def test_should_update_contact(self, sevk):
        """Should update a contact"""
        email = f"test-{uuid.uuid4()}@example.com"
        created = sevk.contacts.create(email=email)
        updated = sevk.contacts.update(created["id"], subscribed=False)
        assert updated["subscribed"] is False
        # Cleanup
        sevk.contacts.delete(created["id"])

    def test_should_throw_error_for_non_existent_contact(self, sevk):
        """Should throw error for non-existent contact"""
        with pytest.raises(Exception) as exc_info:
            sevk.contacts.get("non-existent-id")
        assert "404" in str(exc_info.value)

    def test_should_delete_contact(self, sevk):
        """Should delete a contact"""
        email = f"test-{uuid.uuid4()}@example.com"
        created = sevk.contacts.create(email=email)
        sevk.contacts.delete(created["id"])
        with pytest.raises(Exception) as exc_info:
            sevk.contacts.get(created["id"])
        assert "404" in str(exc_info.value)


class TestAudiences:
    """Test audiences resource"""

    def test_should_list_audiences(self, sevk):
        """Should list audiences with correct response structure"""
        response = sevk.audiences.list()
        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)

    def test_should_create_audience(self, sevk):
        """Should create an audience with required fields"""
        name = f"Test Audience {uuid.uuid4()}"
        audience = sevk.audiences.create(name=name)
        assert audience["name"] == name
        assert "id" in audience
        # Cleanup
        sevk.audiences.delete(audience["id"])

    def test_should_create_audience_with_all_fields(self, sevk):
        """Should create an audience with all fields"""
        name = f"Full Audience {uuid.uuid4()}"
        audience = sevk.audiences.create(
            name=name,
            description="Test description",
            users_can_see="PUBLIC"
        )
        assert audience["name"] == name
        assert audience["description"] == "Test description"
        assert audience["usersCanSee"] == "PUBLIC"
        # Cleanup
        sevk.audiences.delete(audience["id"])

    def test_should_get_audience(self, sevk):
        """Should get an audience by id"""
        name = f"Test Audience {uuid.uuid4()}"
        created = sevk.audiences.create(name=name)
        audience = sevk.audiences.get(created["id"])
        assert audience["id"] == created["id"]
        assert audience["name"] == name
        # Cleanup
        sevk.audiences.delete(created["id"])

    def test_should_update_audience(self, sevk):
        """Should update an audience"""
        name = f"Test Audience {uuid.uuid4()}"
        created = sevk.audiences.create(name=name)
        new_name = f"Updated Audience {uuid.uuid4()}"
        updated = sevk.audiences.update(created["id"], name=new_name)
        assert updated["name"] == new_name
        # Cleanup
        sevk.audiences.delete(created["id"])

    def test_should_add_contacts_to_audience(self, sevk):
        """Should add contacts to audience"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        contact = sevk.contacts.create(email=f"test-{uuid.uuid4()}@example.com")
        result = sevk.audiences.add_contacts(audience["id"], [contact["id"]])
        assert result is not None
        # Cleanup
        sevk.contacts.delete(contact["id"])
        sevk.audiences.delete(audience["id"])

    def test_should_delete_audience(self, sevk):
        """Should delete an audience"""
        name = f"Test Audience {uuid.uuid4()}"
        created = sevk.audiences.create(name=name)
        sevk.audiences.delete(created["id"])
        with pytest.raises(Exception) as exc_info:
            sevk.audiences.get(created["id"])
        assert "404" in str(exc_info.value)


class TestTemplates:
    """Test templates resource"""

    def test_should_list_templates(self, sevk):
        """Should list templates with correct response structure"""
        response = sevk.templates.list()
        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)

    def test_should_create_template(self, sevk):
        """Should create a template with required fields"""
        title = f"Test Template {uuid.uuid4()}"
        content = "<p>Hello World</p>"
        template = sevk.templates.create(title=title, content=content)
        assert template["title"] == title
        assert "id" in template
        # Cleanup
        sevk.templates.delete(template["id"])

    def test_should_get_template(self, sevk):
        """Should get a template by id"""
        title = f"Test Template {uuid.uuid4()}"
        content = "<p>Hello World</p>"
        created = sevk.templates.create(title=title, content=content)
        template = sevk.templates.get(created["id"])
        assert template["id"] == created["id"]
        assert template["title"] == title
        # Cleanup
        sevk.templates.delete(created["id"])

    def test_should_update_template(self, sevk):
        """Should update a template"""
        title = f"Test Template {uuid.uuid4()}"
        content = "<p>Hello World</p>"
        created = sevk.templates.create(title=title, content=content)
        new_title = f"Updated Template {uuid.uuid4()}"
        updated = sevk.templates.update(created["id"], title=new_title)
        assert updated["title"] == new_title
        # Cleanup
        sevk.templates.delete(created["id"])

    def test_should_duplicate_template(self, sevk):
        """Should duplicate a template"""
        title = f"Test Template {uuid.uuid4()}"
        content = "<p>Hello World</p>"
        created = sevk.templates.create(title=title, content=content)
        duplicated = sevk.templates.duplicate(created["id"])
        assert duplicated["id"] != created["id"]
        # Cleanup
        sevk.templates.delete(created["id"])
        sevk.templates.delete(duplicated["id"])

    def test_should_delete_template(self, sevk):
        """Should delete a template"""
        title = f"Test Template {uuid.uuid4()}"
        content = "<p>Hello World</p>"
        created = sevk.templates.create(title=title, content=content)
        sevk.templates.delete(created["id"])
        with pytest.raises(Exception) as exc_info:
            sevk.templates.get(created["id"])
        assert "404" in str(exc_info.value)


class TestBroadcasts:
    """Test broadcasts resource"""

    def test_should_list_broadcasts(self, sevk):
        """Should list broadcasts with correct response structure"""
        response = sevk.broadcasts.list()
        assert "items" in response
        assert "total" in response
        assert isinstance(response["items"], list)

    def test_should_list_broadcasts_with_pagination(self, sevk):
        """Should list broadcasts with pagination"""
        response = sevk.broadcasts.list(page=1, limit=5)
        assert response["page"] == 1
        assert len(response["items"]) <= 5

    def test_should_list_broadcasts_with_search(self, sevk):
        """Should list broadcasts with search"""
        response = sevk.broadcasts.list(search="test")
        assert "items" in response
        assert isinstance(response["items"], list)


class TestDomains:
    """Test domains resource"""

    def test_should_list_domains(self, sevk):
        """Should list domains with correct response structure"""
        response = sevk.domains.list()
        assert "domains" in response
        assert isinstance(response["domains"], list)

    def test_should_list_only_verified_domains(self, sevk):
        """Should list only verified domains"""
        response = sevk.domains.list(verified=True)
        assert "domains" in response
        assert isinstance(response["domains"], list)
        # All returned domains should be verified
        for domain in response["domains"]:
            assert domain["verified"] is True


class TestTopics:
    """Test topics resource"""

    def test_should_list_topics(self, sevk):
        """Should list topics for an audience"""
        # Create audience first
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        response = sevk.topics.list(audience["id"])
        assert "items" in response
        assert isinstance(response["items"], list)
        # Cleanup
        sevk.audiences.delete(audience["id"])

    def test_should_create_topic(self, sevk):
        """Should create a topic"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        topic = sevk.topics.create(audience["id"], name=f"Test Topic {uuid.uuid4()}")
        assert "id" in topic
        assert "name" in topic
        # Cleanup
        sevk.topics.delete(audience["id"], topic["id"])
        sevk.audiences.delete(audience["id"])

    def test_should_get_topic(self, sevk):
        """Should get a topic by id"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        created = sevk.topics.create(audience["id"], name=f"Test Topic {uuid.uuid4()}")
        topic = sevk.topics.get(audience["id"], created["id"])
        assert topic["id"] == created["id"]
        # Cleanup
        sevk.topics.delete(audience["id"], topic["id"])
        sevk.audiences.delete(audience["id"])

    def test_should_update_topic(self, sevk):
        """Should update a topic"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        created = sevk.topics.create(audience["id"], name=f"Test Topic {uuid.uuid4()}")
        new_name = f"Updated Topic {uuid.uuid4()}"
        updated = sevk.topics.update(audience["id"], created["id"], name=new_name)
        assert updated["name"] == new_name
        # Cleanup
        sevk.topics.delete(audience["id"], created["id"])
        sevk.audiences.delete(audience["id"])

    def test_should_delete_topic(self, sevk):
        """Should delete a topic"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        created = sevk.topics.create(audience["id"], name=f"Test Topic {uuid.uuid4()}")
        sevk.topics.delete(audience["id"], created["id"])
        with pytest.raises(Exception) as exc_info:
            sevk.topics.get(audience["id"], created["id"])
        assert "404" in str(exc_info.value)
        # Cleanup
        sevk.audiences.delete(audience["id"])


class TestSegments:
    """Test segments resource"""

    def test_should_list_segments(self, sevk):
        """Should list segments for an audience"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        response = sevk.segments.list(audience["id"])
        assert "items" in response
        assert isinstance(response["items"], list)
        # Cleanup
        sevk.audiences.delete(audience["id"])

    def test_should_create_segment(self, sevk):
        """Should create a segment"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        segment = sevk.segments.create(
            audience["id"],
            name=f"Test Segment {uuid.uuid4()}",
            rules=[{"field": "email", "operator": "contains", "value": "@"}],
            operator="AND"
        )
        assert "id" in segment
        assert "name" in segment
        # Cleanup
        sevk.segments.delete(audience["id"], segment["id"])
        sevk.audiences.delete(audience["id"])

    def test_should_get_segment(self, sevk):
        """Should get a segment by id"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        created = sevk.segments.create(
            audience["id"],
            name=f"Test Segment {uuid.uuid4()}",
            rules=[{"field": "email", "operator": "contains", "value": "@"}],
            operator="AND"
        )
        segment = sevk.segments.get(audience["id"], created["id"])
        assert segment["id"] == created["id"]
        # Cleanup
        sevk.segments.delete(audience["id"], segment["id"])
        sevk.audiences.delete(audience["id"])

    def test_should_update_segment(self, sevk):
        """Should update a segment"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        created = sevk.segments.create(
            audience["id"],
            name=f"Test Segment {uuid.uuid4()}",
            rules=[{"field": "email", "operator": "contains", "value": "@"}],
            operator="AND"
        )
        new_name = f"Updated Segment {uuid.uuid4()}"
        updated = sevk.segments.update(audience["id"], created["id"], name=new_name)
        assert updated["name"] == new_name
        # Cleanup
        sevk.segments.delete(audience["id"], created["id"])
        sevk.audiences.delete(audience["id"])

    def test_should_delete_segment(self, sevk):
        """Should delete a segment"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        created = sevk.segments.create(
            audience["id"],
            name=f"Test Segment {uuid.uuid4()}",
            rules=[{"field": "email", "operator": "contains", "value": "@"}],
            operator="AND"
        )
        sevk.segments.delete(audience["id"], created["id"])
        with pytest.raises(Exception) as exc_info:
            sevk.segments.get(audience["id"], created["id"])
        assert "404" in str(exc_info.value)
        # Cleanup
        sevk.audiences.delete(audience["id"])


class TestSubscriptions:
    """Test subscriptions resource"""

    def test_should_subscribe_contact(self, sevk):
        """Should subscribe a contact"""
        audience = sevk.audiences.create(name=f"Test Audience {uuid.uuid4()}")
        email = f"test-{uuid.uuid4()}@example.com"
        result = sevk.subscriptions.subscribe(email=email, audience_id=audience["id"])
        assert result is not None
        assert "contact" in result
        assert result["contact"]["email"] == email
        # Cleanup
        sevk.audiences.delete(audience["id"])

    def test_should_unsubscribe_contact_by_email(self, sevk):
        """Should unsubscribe a contact by email"""
        # Create and subscribe a contact first
        email = f"unsubscribe-test-{uuid.uuid4()}@example.com"
        contact = sevk.contacts.create(email=email, subscribed=True)

        # Unsubscribe
        sevk.subscriptions.unsubscribe(email=email)

        # Verify unsubscription
        updated_contact = sevk.contacts.get(contact["id"])
        assert updated_contact["subscribed"] is False

        # Cleanup
        sevk.contacts.delete(contact["id"])


class TestEmails:
    """Test emails resource"""

    def test_should_reject_email_with_unverified_domain(self, sevk):
        """Should reject email with unverified domain"""
        with pytest.raises(Exception) as exc_info:
            sevk.emails.send({
                "to": "test@example.com",
                "subject": "Test Email",
                "from": "test@unverified-domain.com",
                "html": "<p>Hello</p>"
            })
        # Should fail due to unverified domain
        error_msg = str(exc_info.value).lower()
        assert "403" in str(exc_info.value) or "domain" in error_msg or "verified" in error_msg

    def test_should_reject_email_with_domain_not_owned_by_project(self, sevk):
        """Should reject email with domain not owned by project"""
        with pytest.raises(Exception) as exc_info:
            sevk.emails.send({
                "to": "test@example.com",
                "subject": "Test Email",
                "from": "no-reply@not-my-domain.io",
                "html": "<p>Hello</p>"
            })
        # Should get 403 Forbidden
        error_msg = str(exc_info.value).lower()
        assert "403" in str(exc_info.value) or "domain" in error_msg

    def test_should_reject_email_with_invalid_from_address(self, sevk):
        """Should reject email with invalid from address"""
        with pytest.raises(Exception) as exc_info:
            sevk.emails.send({
                "to": "test@example.com",
                "subject": "Test Email",
                "from": "invalid-email-without-domain",
                "html": "<p>Hello</p>"
            })
        # Should get 400 Bad Request for invalid email
        assert "400" in str(exc_info.value)

    def test_should_return_proper_error_message_for_domain_verification(self, sevk):
        """Should return proper error message for domain verification"""
        with pytest.raises(Exception) as exc_info:
            sevk.emails.send({
                "to": "recipient@example.com",
                "subject": "Test Email",
                "from": "sender@random-unverified-domain.xyz",
                "html": "<p>Hello World</p>"
            })
        # Error message should contain helpful information
        error_msg = str(exc_info.value).lower()
        assert len(error_msg) > 0
        # Should mention domain verification
        assert "domain" in error_msg or "verified" in error_msg or "forbidden" in error_msg


class TestErrorHandling:
    """Test error handling"""

    def test_should_handle_404_errors_gracefully(self, sevk):
        """Should handle 404 errors gracefully"""
        with pytest.raises(Exception) as exc_info:
            sevk.contacts.get("non-existent-id-12345")
        assert "404" in str(exc_info.value)

    def test_should_handle_validation_errors(self, sevk):
        """Should handle validation errors"""
        with pytest.raises(Exception) as exc_info:
            # Try to create contact with invalid email
            sevk.contacts.create(email="invalid-email")
        assert exc_info.value is not None


class TestMarkupRenderer:
    """Test markup renderer - uses email tag wrapper for proper HTML document output"""

    def test_should_return_html_document_structure(self):
        """Should return HTML document structure"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert "<!DOCTYPE html" in html
        assert "<html" in html
        assert "<head>" in html
        assert "<body" in html
        assert "</html>" in html

    def test_should_include_meta_tags(self):
        """Should include meta tags"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert "charset=UTF-8" in html
        assert "viewport" in html

    def test_should_include_title_when_provided(self):
        """Should include title when provided"""
        from sevk.markup import render
        markup = "<email><head><title>Test Email</title></head><body></body></email>"
        html = render(markup)
        assert "<title>Test Email</title>" in html

    def test_should_include_preview_text_when_provided(self):
        """Should include preview text when provided"""
        from sevk.markup import render
        markup = "<email><head><preview>Preview text here</preview></head><body></body></email>"
        html = render(markup)
        assert "Preview text here" in html
        assert "display:none" in html

    def test_should_include_custom_styles_when_provided(self):
        """Should include custom styles when provided"""
        from sevk.markup import render
        markup = "<email><head><style>.custom { color: red; }</style></head><body></body></email>"
        html = render(markup)
        assert ".custom { color: red; }" in html

    def test_should_render_empty_markup_with_document_structure(self):
        """Should render empty markup with document structure"""
        from sevk.markup import render
        html = render("")
        assert "<!DOCTYPE html" in html
        assert "<body" in html

    def test_should_have_default_body_styles(self):
        """Should have default body styles"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert "margin:0" in html
        assert "padding:0" in html
        assert "font-family" in html

    def test_should_include_html_lang_attribute(self):
        """Should include html lang attribute"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert 'lang="en"' in html

    def test_should_include_html_dir_attribute(self):
        """Should include html dir attribute"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert 'dir="ltr"' in html

    def test_should_include_content_type_meta_tag(self):
        """Should include Content-Type meta tag"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert "Content-Type" in html
        assert "text/html" in html

    def test_should_include_xhtml_doctype(self):
        """Should include XHTML doctype"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert "XHTML 1.0 Transitional" in html

    def test_should_include_background_color_in_body_styles(self):
        """Should include background-color in body styles"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert "background-color" in html

    def test_should_render_mail_tag_same_as_email_tag(self):
        """Should render mail tag same as email tag"""
        from sevk.markup import render
        html = render("<mail><body></body></mail>")
        assert "<!DOCTYPE html" in html
        assert "<body" in html

    def test_should_handle_complex_markup_structure(self):
        """Should handle complex markup structure"""
        from sevk.markup import render
        markup = """<email>
            <head>
                <title>Complex Email</title>
                <preview>This is a preview</preview>
                <style>.test { color: blue; }</style>
            </head>
            <body></body>
        </email>"""
        html = render(markup)
        assert "Complex Email" in html
        assert "This is a preview" in html
        assert ".test { color: blue; }" in html

    def test_should_include_font_links_when_provided(self):
        """Should include font links when provided"""
        from sevk.markup import render
        markup = '<email><head><font name="Roboto" url="https://fonts.googleapis.com/css?family=Roboto" /></head><body></body></email>'
        html = render(markup)
        assert "fonts.googleapis.com" in html

    def test_should_handle_multiple_fonts(self):
        """Should handle multiple fonts"""
        from sevk.markup import render
        markup = '''<email><head>
            <font name="Roboto" url="https://fonts.googleapis.com/css?family=Roboto" />
            <font name="Open Sans" url="https://fonts.googleapis.com/css?family=Open+Sans" />
        </head><body></body></email>'''
        html = render(markup)
        assert "Roboto" in html
        assert "Open+Sans" in html

    def test_should_handle_whitespace_in_markup(self):
        """Should handle whitespace in markup"""
        from sevk.markup import render
        markup = "   <email>   <body>   </body>   </email>   "
        html = render(markup)
        assert "<!DOCTYPE html" in html
        assert "<body" in html

    def test_should_return_string_type(self):
        """Should return string type"""
        from sevk.markup import render
        html = render("<email><body></body></email>")
        assert isinstance(html, str)
        assert len(html) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
