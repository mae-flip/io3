import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { AdminService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

interface DeleteGameProps {
  id: string
  title: string | null | undefined
}

const formSchema = z.object({
  removal_reason: z
    .string()
    .trim()
    .min(1, { message: "Removal reason is required" })
    .max(1000, { message: "Removal reason must be 1000 characters or less" }),
})

type FormData = z.infer<typeof formSchema>

const DeleteGame = ({ id, title }: DeleteGameProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { removal_reason: "" },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      AdminService.deleteAdminGame({
        id,
        requestBody: data,
      }),
    onSuccess: () => {
      showSuccessToast("Game removed from the index")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["adminGames"] })
      queryClient.invalidateQueries({ queryKey: ["adminRemovedGames"] })
      queryClient.invalidateQueries({ queryKey: ["games"] })
    },
  })

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open)
    if (!open) {
      form.reset()
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        className="text-destructive hover:text-destructive"
        onClick={() => setIsOpen(true)}
        aria-label="Remove game"
      >
        <Trash2 className="size-4" />
      </Button>
      <Dialog open={isOpen} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Remove from index</DialogTitle>
            <DialogDescription>
              Remove <strong>{title || "this game"}</strong> from the index?
              You can restore it later from the removed games table.
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit((data) => mutation.mutate(data))}>
              <FormField
                control={form.control}
                name="removal_reason"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Removal reason <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <textarea
                        {...field}
                        rows={4}
                        placeholder="Why is this game being removed from the index?"
                        className={cn(
                          "placeholder:text-muted-foreground border-input w-full min-w-0 rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
                          "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
                          "aria-invalid:ring-destructive/20 aria-invalid:border-destructive",
                        )}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter className="mt-4">
                <DialogClose asChild>
                  <Button variant="outline" disabled={mutation.isPending}>
                    Cancel
                  </Button>
                </DialogClose>
                <LoadingButton
                  variant="destructive"
                  type="submit"
                  loading={mutation.isPending}
                >
                  Remove
                </LoadingButton>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default DeleteGame
