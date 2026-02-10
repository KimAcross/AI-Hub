import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Header } from '@/components/layout/header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { AssistantForm } from '@/components/assistant/assistant-form'
import { TemplateCard } from '@/components/assistant/template-card'
import { useCreateAssistant, useAssistantTemplates, useCreateFromTemplate } from '@/hooks/use-assistants'
import { Skeleton } from '@/components/ui/skeleton'
import type { AssistantCreate, AssistantUpdate } from '@/types'

export function NewAssistantPage() {
  const navigate = useNavigate()
  const createAssistant = useCreateAssistant()
  const createFromTemplate = useCreateFromTemplate()
  const { data: templates, isLoading: templatesLoading } = useAssistantTemplates()

  const handleSubmit = (data: AssistantCreate | AssistantUpdate) => {
    createAssistant.mutate(data as AssistantCreate, {
      onSuccess: (assistant) => {
        navigate(`/assistants/${assistant.id}`)
      },
    })
  }

  const handleUseTemplate = (templateId: string) => {
    createFromTemplate.mutate(
      { templateId },
      {
        onSuccess: (assistant) => {
          navigate(`/assistants/${assistant.id}`)
        },
      }
    )
  }

  return (
    <div className="flex flex-col h-screen">
      <Header title="New Assistant">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
      </Header>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          {/* Templates Section */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-4">Start from a Template</h2>
            {templatesLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <Card key={i}>
                    <CardHeader>
                      <Skeleton className="h-10 w-10 rounded-full mb-2" />
                      <Skeleton className="h-4 w-32" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-4 w-full mb-2" />
                      <Skeleton className="h-4 w-2/3" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : templates && templates.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {templates.map((template) => (
                  <TemplateCard
                    key={template.id}
                    template={template}
                    onUse={() => handleUseTemplate(template.id)}
                    isLoading={createFromTemplate.isPending}
                  />
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No templates available</p>
            )}
          </div>

          {/* Custom Form */}
          <Card>
            <CardHeader>
              <CardTitle>Create Custom Assistant</CardTitle>
              <CardDescription>
                Build your own assistant from scratch
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AssistantForm
                onSubmit={handleSubmit}
                onCancel={() => navigate(-1)}
                isLoading={createAssistant.isPending}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
